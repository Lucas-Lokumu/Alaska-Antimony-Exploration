# Alaska Antimony Exploration

Data-driven multicriteria assessment of antimony exploration potential in Alaska using USGS mineral occurrences, historical grades and tonnages, stream-sediment geochemistry, Python and QGIS.

## Project overview

This project develops an exploratory multicriteria framework to identify and rank antimony sites in Alaska that may justify further geological investigation.

The analysis combines historical mining records, documented antimony grades and tonnages, regional stream-sediment geochemistry and geological context.

Python was used for data cleaning, filtering, scoring and statistical analysis. QGIS was used for spatial analysis and map production.

The project is intended as an exploration-screening study. It does not constitute a mineral resource estimate, reserve estimate, feasibility study or economic valuation.

## Research question

How can heterogeneous historical mining records and regional geochemical data be combined to produce a transparent comparative ranking of antimony exploration sites in Alaska?

## Objectives

The main objectives are to:

- identify antimony-related mineral occurrences in the Alaska Resource Data File;
- distinguish antimony as a main commodity, secondary commodity or stibnite-only mention;
- consolidate available historical grades and tonnages;
- analyze antimony concentrations in stream-sediment samples;
- identify moderate, high and very high geochemical anomalies;
- compare documented sites with nearby anomalies;
- construct a transparent multicriteria ranking;
- map the final exploration priorities.

## Data sources

The project uses publicly available data from the following sources:

### USGS Alaska Resource Data File

The Alaska Resource Data File provides information on mineral occurrences, prospects and historical mines in Alaska.

Variables used include:

- site name;
- main and secondary commodities;
- mineral descriptions;
- site type;
- production status;
- coordinates;
- historical grade and tonnage information.

### USGS Alaska Geochemical Database Version 4.0

The Alaska Geochemical Database Version 4.0 provides analytical results for geological samples collected across Alaska.

This project uses stream-sediment samples analyzed for antimony.

### USGS Geologic Map of Alaska

The generalized geological map of Alaska, Scientific Investigations Map 3340, is used to provide regional geological context.

The geological layer is descriptive only and is not directly weighted in the final score.

### OpenStreetMap

OpenStreetMap is used as a reference basemap for the QGIS maps.

Large raw datasets are not stored directly in this repository.

See [`data/README.md`](data/README.md) for additional information.

## Data preparation

The original ARDF dataset contained 7,720 records.

The filtering process identified:

- 289 records with antimony as a main commodity;
- 573 records with antimony as a secondary commodity;
- 512 records containing a stibnite mention.

Because these groups partially overlap, duplicates were removed and the records were harmonized.

The final filtered dataset contains:

- 887 antimony-related occurrences;
- 289 main-commodity occurrences;
- 569 secondary-commodity occurrences;
- 29 occurrences retained through stibnite mentions only.

Historical grade and tonnage information was consolidated into:

- 18 observations;
- 13 documented sites.

## Stream-sediment geochemistry

The AGDB4 extraction contains 129,074 stream-sediment samples.

Among these samples:

- 28,968 contain a measured antimony value;
- 91,212 are below the analytical detection limit;
- 8,894 contain no usable antimony value.

For measured values:

- median: 1.4 ppm;
- 95th percentile: 14.8 ppm;
- 98th percentile: 50 ppm;
- maximum observed value: approximately 100,000.11 ppm.

A total of 3,110 antimony anomalies were identified:

- 1,660 moderate anomalies;
- 741 high anomalies;
- 709 very high anomalies.

For map visualization only, 23 values above 5,000 ppm were visually capped at 5,000 ppm. The original values were not modified in the data.

## Methodology

The final ranking combines two components:

```text
Final score = site screening score + geochemical score
