# google-maps-distance

In this project I'm exploring how to use google's Distance Matrix API.  
Later I decided to explore [openrouteservice](https://openrouteservice.org/) based on tip from Brecht Van Maldergem.  
During a conversation with Marco Branzi, I learned [TomTom](https://developer.tomtom.com/routing-api/documentation/matrix-routing-v2/matrix-routing-v2-service) offers the same service too

## Making sense of the data & see results

**Just look at the [notebook](explore.ipynb)**

## Repo structure

1. `explore.ipynb` where I explore data and try to make sense of things
1. `districts.py` generates a dataset with districts close to your home location
1. `shops.py` generates a dataset with Colruyt Group shops near your home location
1. `distance.py` uses districts & shops to calculate origin & destination travel times
1. `tomtom.py` is a client for talking to the tomtom api

## Initial setup

* build the environment specified in `environment.yml` with conda or mamba
* download the nis_district data from government

```bash
wget https://statbel.fgov.be/sites/default/files/files/opendata/Statistische%20sectoren/sh_statbel_statistical_sectors_3812_20220101.shp.zip
```

* add the `api_google.key` file to the repo (one line, with just your key)
* add the `api_openrouteservice.key` file to the repo (one line, with just your key)
* add the `api_tomtom.key` file to the repo (one line, with just your key)

## Producing drive times

1. use `districts.py` and `shops.py` to build the parquet files with relevant data
1. run `distance.py` to generate drive times and store results
1. results are stored in `traveltime_shops_near_home.pickle`
