# QGIS project

This folder contains the QGIS project and related documentation used for the spatial analysis and map production.

## Main spatial layers

The project uses:

- antimony-related ARDF occurrences;
- historical grade locations;
- AGDB4 stream-sediment antimony anomalies;
- final ranked exploration sites;
- generalized geological units of Alaska;
- administrative boundaries;
- reference cities;
- OpenStreetMap basemap.

## Maps produced

The QGIS project was used to create:

1. a map of antimony occurrences;
2. a map of documented historical grades;
3. a map of stream-sediment antimony anomalies;
4. a map of final exploration priorities.

## Coordinate systems

The original datasets may use different coordinate reference systems.

Before spatial analysis, the layers should be checked and reprojected into a suitable common coordinate reference system.

## File paths

The QGIS project may contain local file paths from the original working environment.

Users opening the project on another computer may need to reconnect the layers manually.

## Data availability

Large raw spatial datasets are not stored directly in this repository.

See `data/README.md` for the official sources and download information.

## Important note

The geological layer is used as regional descriptive context only. It is not directly included as a weighted component of the final score.
