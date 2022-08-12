from distance import import_origins_destinations, get_points_as_list

# define imput files
list_input_files = ["districts_near_my_home.parquet", "shops_near_my_home.parquet"]

# get origin & destination data
gdf_districts, gdf_shops = import_origins_destinations(*list_input_files)

my_origins = get_points_as_list(gdf_districts["center"])

# print
print(my_origins)
print(type(my_origins[0]))
