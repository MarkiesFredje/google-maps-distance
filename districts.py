# wget https://statbel.fgov.be/sites/default/files/files/opendata/Statistische%20sectoren/sh_statbel_statistical_sectors_3812_20220101.shp.zip

from geopandas import read_file
from shapely.geometry import Point

# where I live
P_HOME_FRED = Point( 4.232616769580238, 50.732355613106265)

# Loading 2022 shp's
gdf_belgium = read_file('zip://sh_statbel_statistical_sectors_3812_20220101.shp.zip!sh_statbel_statistical_sectors_3812_20220101.shp/sh_statbel_statistical_sectors_3812_20220101.shp')
gdf_belgium = gdf_belgium.to_crs('EPSG:4326')

# Finding the closest districts to where I live
n_districts = 10
gdf_home_fred = gdf_belgium.loc[gdf_belgium.distance(P_HOME_FRED).sort_values().index[:n_districts]]

# Save results as parquet file
gdf_home_fred.to_parquet('districts_near_my_home.parquet')
