from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

GRADES_FILE = Path("data_processed/antimony_grades_analyzed.csv")
OCCURRENCES_FILE = Path("data_processed/antimony_occurrences_ardf.csv")
OUTPUT_FILE = Path("data_processed/antimony_grades_mapped.csv")


# ------------------------------------------------------------
# 2. Lecture
# ------------------------------------------------------------

grades = pd.read_csv(
    GRADES_FILE,
    encoding="utf-8-sig",
)

occurrences = pd.read_csv(
    OCCURRENCES_FILE,
    encoding="utf-8-sig",
    low_memory=False,
)


# ------------------------------------------------------------
# 3. Nettoyage des noms de sites
# ------------------------------------------------------------

grades["site_key"] = (
    grades["site"]
    .astype("string")
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)

occurrences["site_key"] = (
    occurrences["site"]
    .astype("string")
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)


# ------------------------------------------------------------
# 4. Colonnes ARDF à conserver
# ------------------------------------------------------------

coordinates = occurrences[
    [
        "site_key",
        "ARDF_number",
        "site",
        "latitude",
        "longitude_for_GIS",
        "site_type",
        "antimony_category",
    ]
].drop_duplicates(subset=["site_key"])


# ------------------------------------------------------------
# 5. Jointure
# ------------------------------------------------------------

mapped = grades.merge(
    coordinates,
    on="site_key",
    how="left",
    suffixes=("_grade", "_ardf"),
)


# ------------------------------------------------------------
# 6. Contrôle des sites sans coordonnées
# ------------------------------------------------------------

missing_coordinates = mapped[
    mapped["latitude"].isna()
    | mapped["longitude_for_GIS"].isna()
].copy()

print(f"Nombre d'observations de teneur : {len(mapped)}")
print(
    "Observations sans coordonnées : "
    f"{len(missing_coordinates)}"
)

if not missing_coordinates.empty:
    print("\nSites sans correspondance :")
    print(
        missing_coordinates[
            ["site_grade"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )


# ------------------------------------------------------------
# 7. Sélection finale
# ------------------------------------------------------------

final_columns = [
    "ARDF_number",
    "site_grade",
    "site_ardf",
    "latitude",
    "longitude_for_GIS",
    "site_type",
    "antimony_category",
    "data_source",
    "sb_grade_min",
    "sb_grade_max",
    "sb_grade_mid",
    "grade_unit",
    "tonnage",
    "tonnage_unit",
    "tonnage_metric_tonnes",
    "contained_sb_metric_tonnes",
    "data_context",
    "resource_category",
    "year",
    "notes",
    "data_quality",
]

mapped = mapped[final_columns]


# ------------------------------------------------------------
# 8. Export
# ------------------------------------------------------------

mapped.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)

missing_coordinates.to_csv(
    "data_processed/antimony_grades_unmatched.csv",
    index=False,
    encoding="utf-8-sig",
)

print(f"\nFichier créé : {OUTPUT_FILE}")