from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

INPUT_FILE = Path("data_processed/antimony_grades_mapped.csv")
OUTPUT_FILE = Path("data_processed/antimony_site_screening.csv")


# ------------------------------------------------------------
# 2. Lecture
# ------------------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
)

text_columns = [
    "site_grade",
    "data_context",
    "resource_category",
    "tonnage_unit",
]

for column in text_columns:
    if column in df.columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )


# ------------------------------------------------------------
# 3. Score de qualité documentaire
# ------------------------------------------------------------

context_score = {
    "resource_average": 5,
    "production_average": 4,
    "production_grade": 4,
    "shipment_grade": 3,
    "historical_estimate": 3,
    "sample_grade": 2,
    "contained_metal": 2,
    "unknown": 1,
}

df["documentation_score"] = (
    df["data_context"]
    .map(context_score)
    .fillna(1)
)


# ------------------------------------------------------------
# 4. Indicateurs par observation
# ------------------------------------------------------------

df["has_grade"] = df["sb_grade_mid"].notna()
df["has_tonnage"] = df["tonnage"].notna()

df["quantitative_score"] = (
    df["has_grade"].astype(int)
    + df["has_tonnage"].astype(int)
)


# ------------------------------------------------------------
# 5. Agrégation par site
# ------------------------------------------------------------

screening = (
    df.groupby("site_grade", dropna=False)
    .agg(
        ARDF_number=("ARDF_number", "first"),
        latitude=("latitude", "first"),
        longitude_for_GIS=("longitude_for_GIS", "first"),
        site_type=("site_type", "first"),
        antimony_category=("antimony_category", "first"),

        number_of_records=("site_grade", "size"),

        grade_min_percent=("sb_grade_min", "min"),
        grade_max_percent=("sb_grade_max", "max"),
        grade_mean_percent=("sb_grade_mid", "mean"),

        documented_tonnage=("tonnage", "max"),
        tonnage_unit=("tonnage_unit", "first"),

        metric_tonnage=("tonnage_metric_tonnes", "max"),
        contained_sb_metric_tonnes=(
            "contained_sb_metric_tonnes",
            "max",
        ),

        best_documentation_score=(
            "documentation_score",
            "max",
        ),

        quantitative_score=(
            "quantitative_score",
            "max",
        ),

        main_data_context=(
            "data_context",
            lambda values: ", ".join(
                sorted(set(values.dropna().astype(str)))
            ),
        ),
    )
    .reset_index()
)

# ------------------------------------------------------------
# 6. Scores de présélection
# ------------------------------------------------------------

def grade_score(value):
    if pd.isna(value):
        return 0
    if value >= 50:
        return 5
    if value >= 30:
        return 4
    if value >= 15:
        return 3
    if value >= 10:
        return 2
    return 1


def tonnage_score(value):
    if pd.isna(value):
        return 0
    if value >= 5000:
        return 5
    if value >= 1000:
        return 4
    if value >= 100:
        return 3
    if value >= 10:
        return 2
    return 1


screening["grade_score"] = (
    screening["grade_mean_percent"]
    .apply(grade_score)
)

screening["tonnage_score"] = (
    screening["documented_tonnage"]
    .apply(tonnage_score)
)

screening["screening_score"] = (
    screening["grade_score"]
    + screening["tonnage_score"]
    + screening["best_documentation_score"]
    + screening["quantitative_score"]
)


# ------------------------------------------------------------
# 7. Classe de priorité
# ------------------------------------------------------------

def priority_class(score):
    if score >= 14:
        return "High priority"
    if score >= 10:
        return "Medium priority"
    return "Low priority"


screening["screening_priority"] = (
    screening["screening_score"]
    .apply(priority_class)
)

# ------------------------------------------------------------
# 8. Tri et export
# ------------------------------------------------------------

screening = screening.sort_values(
    by=[
        "screening_score",
        "grade_mean_percent",
    ],
    ascending=[False, False],
)

screening.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 9. Résultats
# ------------------------------------------------------------

print(f"Nombre de sites : {len(screening)}")

print("\nClassement de présélection :")
print(
    screening[
        [
            "site_grade",
            "grade_mean_percent",
            "documented_tonnage",
            "tonnage_unit",
            "screening_score",
            "screening_priority",
        ]
    ]
    .to_string(index=False)
)

print(f"\nFichier créé : {OUTPUT_FILE}")