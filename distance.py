from typing import Tuple
from datetime import datetime
from geopandas import read_parquet, geodataframe
from googlemaps import Client
from googlemaps.convert import encode_polyline, decode_polyline  # lat, lng 50,4
from joblib import load, dump


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


def get_points_as_list(s_points) -> list:
    """Transform geopandas series of points to list of coordinate tuples"""
    longs = s_points.x.to_list()
    lats = s_points.y.to_list()
    return [tuple(z) for z in zip(lats, longs)]


if __name__ == "__main__":

    # define imput files
    list_input_files = ["districts_near_my_home.parquet", "shops_near_my_home.parquet"]

    # get origin & destination data
    gdf_districts, gdf_shops = import_origins_destinations(*list_input_files)
    list_origins = get_points_as_list(gdf_districts["center"])
    list_destinations = get_points_as_list(gdf_shops["geometry"])
    print(len(list_origins), len(list_destinations))

    # get api keys
    key_google = get_api_key("api_google.key")

    # create google api client
    try:
        drive_times = load("google_drive_times.pickle")
    except FileNotFoundError:
        g_api = Client(key=key_google)
        drive_times = g_api.distance_matrix(
            origins=list_origins,
            destinations=list_destinations[:10],
            mode="driving",
            avoid="highways",
            units="metric",
            arrival_time=datetime(year=2022, month=8, day=12, hour=17),
        )
        dump(drive_times, "google_drive_times.pickle")
