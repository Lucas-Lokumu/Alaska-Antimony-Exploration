# Python scripts

This folder contains the Python scripts used to process the data and produce the main results of the project.

The scripts cover the following stages:

1. identification of antimony-related occurrences in the Alaska Resource Data File;
2. analysis of site types and production status;
3. extraction and consolidation of historical antimony grades and tonnages;
4. construction of the site screening score;
5. extraction and analysis of stream-sediment antimony concentrations from AGDB4;
6. identification of geochemical anomalies;
7. spatial comparison between documented sites and nearby anomalies;
8. construction of the final multicriteria ranking;
9. production of the final ranking figure.

## Main scripts

- `01_filter_antimony_occurrences.py`  
  Filters the ARDF database to retain sites related to antimony or stibnite.

- `02_analyze_antimony_sites.py`  
  Summarizes site types and historical production status.

- `03_analyze_antimony_grades.py`  
  Extracts and analyzes historical antimony grades and tonnages.

- `04_join_grades_coordinates.py`  
  Associates the consolidated grade data with site coordinates.

- `05_build_site_screening.py`  
  Builds the preliminary site screening score from grade, tonnage, documentation quality and data completeness.

- `08_extract_stream_sediment_sb.py`  
  Extracts antimony values from stream-sediment samples in AGDB4.

- `09_check_sb_extreme_values.py`  
  Reviews extreme antimony concentrations and data quality issues.

- `10_export_sb_anomalies.py`  
  Classifies and exports moderate, high and very high geochemical anomalies.

- `11_compare_sites_sb_anomalies.py`  
  Compares the documented sites with nearby antimony anomalies and calculates the geochemical score.

- `12_build_final_ranking.py`  
  Combines the screening and geochemical scores to produce the final ranking.

- `13_plot_final_ranking.py`  
  Produces the final ranking chart.

## Execution order

The recommended execution order is:

```text
01 → 02 → 03 → 04 → 05 → 08 → 09 → 10 → 11 → 12 → 13
