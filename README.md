# Alaska Antimony Exploration

Data-driven multicriteria assessment of antimony exploration potential in Alaska using USGS mineral occurrences, historical grades and tonnages, stream-sediment geochemistry, Python and QGIS.

## Project overview

This project develops an exploratory screening framework to identify and rank antimony sites in Alaska that may justify further geological investigation.

The analysis combines:

- mineral occurrences from the USGS Alaska Resource Data File;
- historical antimony grades and documented tonnages;
- stream-sediment geochemical data from AGDB4;
- proximity to moderate, high and very high antimony anomalies;
- regional geological context;
- Python-based data processing;
- QGIS spatial analysis and map production.

The project is intended as a comparative exploration-priority assessment. It does not constitute a mineral resource estimate, reserve estimate, feasibility study or economic valuation.

## Research question

How can heterogeneous historical mining records and regional geochemical data be combined to produce a transparent comparative ranking of antimony exploration sites in Alaska?

## Main results

The initial ARDF dataset contained 7,720 records.

After filtering and harmonization:

- 887 antimony-related occurrences were retained;
- 289 records list antimony as a main commodity;
- 569 records list antimony as a secondary commodity;
- 29 records were retained through stibnite mentions only;
- 18 historical grade and tonnage observations were consolidated;
- 13 sites were included in the detailed multicriteria ranking;
- 129,074 stream-sediment samples were reviewed;
- 3,110 antimony anomalies were identified;
- 7 sites received a high final priority;
- 5 sites received a medium final priority;
- 1 site received a low final priority.

The highest-ranked sites are:

1. Scrafford; Treasure Creek — 25
2. Pringle Bench; Jones & Boyle — 25
3. Slate Creek; Taylor mine — 24
4. Eureka Stibnite (Pick claim group) — 23
5. McCarty; American Eagle — 23
6. Stampede — 21
7. Hindenburg; Markovich — 21

Sites with identical scores should be considered tied.

## Methodology

The final score combines two components:

```text
Final score = site screening score + geochemical score
