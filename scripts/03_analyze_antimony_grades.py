from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

INPUT_FILE = Path("data_processed/antimony_grades_curated.csv")
OUTPUT_DIR = Path("data_processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Lecture du fichier
# ------------------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8",
    decimal=",",
)

print(f"Nombre d'observations : {len(df)}")
print(f"Nombre de sites distincts : {df['site'].nunique()}")


# ------------------------------------------------------------
# 3. Nettoyage des colonnes textuelles
# ------------------------------------------------------------

text_columns = [
    "site",
    "data_source",
    "grade_unit",
    "tonnage_unit",
    "data_context",
    "resource_category",
    "notes",
]

for column in text_columns:
    if column in df.columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )


# ------------------------------------------------------------
# 4. Nettoyage des colonnes numériques
# ------------------------------------------------------------

numeric_columns = [
    "sb_grade_min",
    "sb_grade_max",
    "tonnage",
    "year",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )


# ------------------------------------------------------------
# 5. Calcul de la teneur centrale
# ------------------------------------------------------------

df["sb_grade_mid"] = (
    df["sb_grade_min"] + df["sb_grade_max"]
) / 2


# ------------------------------------------------------------
# 6. Conversion des tonnages en tonnes métriques
# ------------------------------------------------------------

def convert_to_metric_tonnes(row):
    """
    Convertit les unités explicites en tonnes métriques.

    Les valeurs simplement notées 'ton' ou 'tons' ne sont pas
    converties, car les sources historiques ne précisent pas
    toujours s'il s'agit de short tons ou de tonnes métriques.
    """

    if pd.isna(row["tonnage"]):
        return float("nan")

    if pd.isna(row["tonnage_unit"]):
        return float("nan")

    unit = str(row["tonnage_unit"]).strip().lower()

    if unit in [
        "tonne",
        "tonnes",
        "metric ton",
        "metric tons",
        "metric tonne",
        "metric tonnes",
    ]:
        return row["tonnage"]

    if unit in [
        "short ton",
        "short tons",
    ]:
        return row["tonnage"] * 0.90718474

    if unit in [
        "kg",
        "kilogram",
        "kilograms",
    ]:
        return row["tonnage"] / 1000

    if unit in [
        "ton",
        "tons",
    ]:
        return float("nan")

    return float("nan")


df["tonnage_metric_tonnes"] = df.apply(
    convert_to_metric_tonnes,
    axis=1,
)


# ------------------------------------------------------------
# 7. Calcul de l'antimoine contenu
# ------------------------------------------------------------

df["contained_sb_metric_tonnes"] = (
    df["tonnage_metric_tonnes"]
    * df["sb_grade_mid"]
    / 100
)


# ------------------------------------------------------------
# 8. Indicateur de qualité documentaire
# ------------------------------------------------------------

def classify_data_quality(row):
    if (
        pd.notna(row["sb_grade_mid"])
        and pd.notna(row["tonnage"])
    ):
        return "Grade and tonnage available"

    if pd.notna(row["sb_grade_mid"]):
        return "Grade only"

    if pd.notna(row["tonnage"]):
        return "Tonnage only"

    return "Insufficient quantitative data"


df["data_quality"] = df.apply(
    classify_data_quality,
    axis=1,
)


# ------------------------------------------------------------
# 9. Résumé par contexte documentaire
# ------------------------------------------------------------

context_summary = (
    df.groupby(
        "data_context",
        dropna=False,
    )
    .agg(
        number_of_records=("site", "size"),
        number_of_sites=("site", "nunique"),
        mean_grade_percent=("sb_grade_mid", "mean"),
        median_grade_percent=("sb_grade_mid", "median"),
        minimum_grade_percent=("sb_grade_min", "min"),
        maximum_grade_percent=("sb_grade_max", "max"),
    )
    .reset_index()
)


# ------------------------------------------------------------
# 10. Résumé des teneurs par site
# ------------------------------------------------------------

grade_summary = (
    df.dropna(subset=["sb_grade_mid"])
    .groupby("site")
    .agg(
        number_of_records=("site", "size"),
        mean_grade_percent=("sb_grade_mid", "mean"),
        minimum_grade_percent=("sb_grade_min", "min"),
        maximum_grade_percent=("sb_grade_max", "max"),
        total_documented_tonnage=("tonnage", "sum"),
    )
    .reset_index()
    .sort_values(
        by="mean_grade_percent",
        ascending=False,
    )
)


# ------------------------------------------------------------
# 11. Résumé des tonnages par site et unité d'origine
# ------------------------------------------------------------

tonnage_summary = (
    df.dropna(subset=["tonnage"])
    .groupby(
        ["site", "tonnage_unit"],
        dropna=False,
    )
    .agg(
        documented_tonnage=("tonnage", "sum"),
        number_of_records=("tonnage", "size"),
    )
    .reset_index()
)


# ------------------------------------------------------------
# 12. Résumé des données converties en tonnes métriques
# ------------------------------------------------------------

metric_summary = (
    df.dropna(subset=["tonnage_metric_tonnes"])
    .groupby("site")
    .agg(
        number_of_records=("site", "size"),
        total_metric_tonnage=(
            "tonnage_metric_tonnes",
            "sum",
        ),
        estimated_contained_sb_metric_tonnes=(
            "contained_sb_metric_tonnes",
            "sum",
        ),
    )
    .reset_index()
    .sort_values(
        by="estimated_contained_sb_metric_tonnes",
        ascending=False,
    )
)


# ------------------------------------------------------------
# 13. Détection des doublons exacts
# ------------------------------------------------------------

duplicate_columns = [
    "site",
    "data_source",
    "sb_grade_min",
    "sb_grade_max",
    "tonnage",
    "tonnage_unit",
    "data_context",
    "year",
]

duplicates = (
    df[
        df.duplicated(
            subset=duplicate_columns,
            keep=False,
        )
    ]
    .sort_values("site")
)


# ------------------------------------------------------------
# 14. Exports
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_DIR / "antimony_grades_analyzed.csv",
    index=False,
    encoding="utf-8-sig",
)

context_summary.to_csv(
    OUTPUT_DIR / "summary_grades_by_context.csv",
    index=False,
    encoding="utf-8-sig",
)

grade_summary.to_csv(
    OUTPUT_DIR / "summary_grades_by_site.csv",
    index=False,
    encoding="utf-8-sig",
)

tonnage_summary.to_csv(
    OUTPUT_DIR / "summary_tonnage_by_site_and_unit.csv",
    index=False,
    encoding="utf-8-sig",
)

metric_summary.to_csv(
    OUTPUT_DIR / "summary_metric_tonnage_and_contained_sb.csv",
    index=False,
    encoding="utf-8-sig",
)

duplicates.to_csv(
    OUTPUT_DIR / "possible_grade_duplicates.csv",
    index=False,
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 15. Résultats dans le terminal
# ------------------------------------------------------------

print("\nQualité des données :")
print(
    df["data_quality"]
    .value_counts()
    .to_string()
)

print("\nRésumé par contexte :")
print(
    context_summary.to_string(
        index=False,
    )
)

print("\nSites classés par teneur centrale :")
print(
    grade_summary[
        [
            "site",
            "mean_grade_percent",
            "minimum_grade_percent",
            "maximum_grade_percent",
        ]
    ]
    .head(15)
    .to_string(index=False)
)

print("\nSites avec tonnage converti en tonnes métriques :")
if metric_summary.empty:
    print("Aucune unité explicitement convertible.")
else:
    print(
        metric_summary.head(15).to_string(
            index=False,
        )
    )

print("\nNombre de doublons potentiels :")
print(len(duplicates))

print("\nFichiers créés :")
print("- data_processed/antimony_grades_analyzed.csv")
print("- data_processed/summary_grades_by_context.csv")
print("- data_processed/summary_grades_by_site.csv")
print("- data_processed/summary_tonnage_by_site_and_unit.csv")
print("- data_processed/summary_metric_tonnage_and_contained_sb.csv")
print("- data_processed/possible_grade_duplicates.csv")