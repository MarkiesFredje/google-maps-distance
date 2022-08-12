from typing import Tuple
from geopandas import read_parquet, geodataframe


def import_origins_destinations(
    origins: str, destinations: str
) -> tuple[geodataframe, geodataframe]:
    """return origins & destinations geodataframes"""
    return read_parquet(origins), read_parquet(destinations)


if __name__ == "__main__":

    # define imput files
    list_input_files = ["districts_near_my_home.parquet", "shops_near_my_home.parquet"]

    # get origin & destination data
    gdf_districts, gdf_shops = import_origins_destinations(*list_input_files)

    print(gdf_districts.shape, gdf_shops.shape)
