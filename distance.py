from time import timezone
from typing import Tuple
from datetime import datetime, timezone
from numpy import asarray
from pandas import DataFrame, json_normalize
from geopandas import read_parquet, geodataframe
from googlemaps import Client as Google
from openrouteservice import Client as openrouteservice
from tomtom import Client as tomtom
from googlemaps.convert import encode_polyline, decode_polyline  # lat, lng 50,4
from joblib import load, dump

N_DESTINATION = 10


def import_origins_destinations(
    origins: str, destinations: str
) -> tuple[geodataframe, geodataframe]:
    """return origins & destinations geodataframes"""
    return read_parquet(origins), read_parquet(destinations)


def get_api_key(service: str) -> str:
    """get the api key for a service"""
    with open(service, "r") as f:
        key = f.read().strip()
    return key


def get_points_as_list(s_points, order="lat-lng") -> list:
    """Transform geopandas series of points to list of coordinate tuples"""
    longs = s_points.x.to_list()
    lats = s_points.y.to_list()
    match order:
        case "lat-lng":
            return [tuple(z) for z in zip(lats, longs)]
        case "lng-lat":
            return [tuple(z) for z in zip(longs, lats)]
        case _:
            raise ValueError("pick 'lat-lng' or 'lng-lat'")


if __name__ == "__main__":

    # define imput files
    list_input_files = ["districts_near_my_home.parquet", "shops_near_my_home.parquet"]

    # get origin & destination data (10 orgins & 50 destinations)
    gdf_districts, gdf_shops = import_origins_destinations(*list_input_files)
    list_origins_lat_lng = get_points_as_list(gdf_districts["center"], order="lat-lng")
    list_destinations_lat_lng = get_points_as_list(
        gdf_shops["geometry"], order="lat-lng"
    )
    list_origins_lng_lat = get_points_as_list(gdf_districts["center"], order="lng-lat")
    list_destinations_lng_lat = get_points_as_list(
        gdf_shops["geometry"], order="lng-lat"
    )

    # get api keys
    key_google = get_api_key("api_google.key")
    key_openrouteservice = get_api_key("api_openrouteservice.key")
    key_tomtom = get_api_key("api_tomtom.key")

    # create google api client
    try:
        drive_times_google = load("google_drive_times.pickle")
    except FileNotFoundError:
        g_api = Google(key=key_google)
        # len(orgigins) * len(destination) <= 100
        drive_times_google = g_api.distance_matrix(
            origins=list_origins_lat_lng,
            destinations=list_destinations_lat_lng[:N_DESTINATION],
            mode="driving",
            avoid="highways",
            units="metric",
            arrival_time=datetime(year=2022, month=8, day=19, hour=17),
        )
        dump(drive_times_google, "google_drive_times.pickle")

    # create openrouteservice api client
    try:
        drive_times_ors = load("openrouteservice_drive_times.pickle")
    except FileNotFoundError:
        ors_api = openrouteservice(key=key_openrouteservice)
        locations = list_origins_lng_lat + list_destinations_lng_lat[:N_DESTINATION]
        drive_times_ors = ors_api.distance_matrix(
            locations=locations,
            sources=list(range(N_DESTINATION)),
            destinations=list(range(N_DESTINATION, len(locations))),
            metrics=["distance", "duration"],
            profile="driving-car",
            resolve_locations=True,
        )
        dump(drive_times_ors, "openrouteservice_drive_times.pickle")

    # create tomtom api client
    try:
        drive_times_tomtom = load("tomtom_drive_times.pickle")
    except FileNotFoundError:
        tt_api = tomtom(key=key_tomtom)
        drive_times_tomtom = tt_api.synchronous_matrix(
            origins=list_origins_lat_lng,
            destinations=list_destinations_lat_lng[:N_DESTINATION],
            arrive_at=datetime(
                year=2022,
                month=8,
                day=19,
                hour=17,
            ),
            route_type="fastest",
            traffic="historical",
            travel_mode="car",
            avoid="tollRoads",
        )
        dump(drive_times_tomtom, "tomtom_drive_times.pickle")

    # prepare dataframe for origin destination traveltimes
    gdf_origins = gdf_districts.rename(
        columns={"geometry": "nis_geometry", "center": "o_centroid_lng_lat"}
    )
    gdf_destination = gdf_shops.iloc[:N_DESTINATION].rename(
        columns={"geometry": "d_centroid_lng_lat", "name": "shop_name"}
    )
    gdf_origins["o_g_address"] = drive_times_google["origin_addresses"]
    gdf_destination["d_g_address"] = drive_times_google["destination_addresses"]
    gdf_traveltime = gdf_origins.merge(gdf_destination, how="cross")

    # process results from google
    df_google_traveltime = json_normalize(
        drive_times_google, record_path=["rows", "elements"]
    )
    gdf_traveltime["g_distance_m"] = df_google_traveltime["distance.value"].to_numpy()
    gdf_traveltime["g_traveltime_s"] = df_google_traveltime["duration.value"].to_numpy()
    gdf_traveltime["g_status"] = df_google_traveltime["status"].to_numpy()

    # process results from openrouteservice
    gdf_traveltime["ors_distance_m"] = asarray(drive_times_ors["distances"]).reshape(
        len(list_origins_lng_lat) * len(list_destinations_lng_lat[:N_DESTINATION]),
    )
    gdf_traveltime["ors_traveltime_s"] = asarray(drive_times_ors["durations"]).reshape(
        len(list_origins_lng_lat) * len(list_destinations_lng_lat[:N_DESTINATION]),
    )

    # process results from tomtom
    df_tomtom_traveltime = json_normalize(drive_times_tomtom["data"])
    df_tomtom_traveltime.sort_values(
        by=["originIndex", "destinationIndex"], inplace=True
    )
    gdf_traveltime["tt_distance_m"] = df_tomtom_traveltime[
        "routeSummary.lengthInMeters"
    ].to_numpy()
    gdf_traveltime["tt_traveltime_s"] = df_tomtom_traveltime[
        "routeSummary.travelTimeInSeconds"
    ].to_numpy()

    # save results
    dump(gdf_traveltime, "traveltime_shops_near_home.pickle")
