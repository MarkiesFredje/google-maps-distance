from requests import get
from pandas import json_normalize
from geopandas import points_from_xy, GeoDataFrame
from shapely.geometry import Point

# where I live
P_HOME_FRED = Point(4.232616769580238, 50.732355613106265)

# url for the shops
URL_SHOPS = (
    "https://ecgplacesmw.colruytgroup.com/ecgplacesmw/v3/nl/places/filter/xtra-all"
)

# Request to api
request = get(URL_SHOPS)
json_data = request.json()

# tranform into dataframe
df_shops = json_normalize(json_data)


# add location as point
gdf_shops = GeoDataFrame(
    df_shops,
    geometry=points_from_xy(
        df_shops["geoCoordinates.longitude"], df_shops["geoCoordinates.latitude"]
    ),
)
dict_rename = {
    "placeId": "place_id",
    "commercialName": "name",
    "branchId": "filiaalnr",
    "geoCoordinates.latitude": "y",
    "geoCoordinates.longitude": "x",
    "address.postalcode": "postcode",
    "geometry": "location",
}
gdf_shops.rename(columns=dict_rename, inplace=True)


# shops near me
cols = [
    "place_id",
    "name",
    "filiaalnr",
    "location",
]
gdf_shops_home = gdf_shops.loc[:, cols]

# save to disk
gdf_shops_home.to_parquet("shops_near_my_home.parquet")
