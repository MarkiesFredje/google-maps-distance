# google-maps-distance

In this project I'm exploring how to use google's Distance Matrix API.  
Later I decided to explore [openrouteservice](https://openrouteservice.org/) based on tip from Brecht Van Maldergem.  

## Repo structure

1. `districts.py` generates a dataset with districts close to your home location
1. `shops.py` generates a dataset with Colruyt Group shops near your home location

## Initial setup

* build the environment specified in `environment.yml` with conda or mamba
* download the nis_district data from government

```bash
wget https://statbel.fgov.be/sites/default/files/files/opendata/Statistische%20sectoren/sh_statbel_statistical_sectors_3812_20220101.shp.zip
```

* add the `api_google.key` file to the repo (one line, with just your key)

## Producing drive times

1. use `districts.py` and `shops.py` to build the parquet files with relevant data
1. todo