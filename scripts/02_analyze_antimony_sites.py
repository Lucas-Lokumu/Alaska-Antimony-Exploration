from pathlib import Path
import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

INPUT_FILE = Path("data_processed/antimony_occurrences_ardf.csv")
OUTPUT_DIR = Path("data_processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Lecture
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Nombre de sites analysés : {len(df):,}")


# ------------------------------------------------------------
# 3. Harmonisation du type de site
# ------------------------------------------------------------

def clean_site_type(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    if value.startswith("mine"):
        return "Mine"
    if value.startswith("prospect"):
        return "Prospect"
    if value.startswith("occurrence"):
        return "Occurrence"

    return "Other"


df["site_type_clean"] = df["site_type"].apply(clean_site_type)


# ------------------------------------------------------------
# 4. Résumé par type de site
# ------------------------------------------------------------

site_type_summary = (
    df["site_type_clean"]
    .value_counts()
    .rename_axis("site_type")
    .reset_index(name="number_of_sites")
)

site_type_summary["share_percent"] = (
    site_type_summary["number_of_sites"] / len(df) * 100
).round(1)

print("\nRépartition par type de site :")
print(site_type_summary.to_string(index=False))


# ------------------------------------------------------------
# 5. Harmonisation de la production
# ------------------------------------------------------------

def clean_production(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip().lower()

    if value.startswith("yes"):
        return "Production reported"
    if value.startswith("no"):
        return "No production reported"
    if "undet" in value:
        return "Undetermined"

    return "Other"


df["production_clean"] = df["production"].apply(clean_production)


production_summary = (
    df["production_clean"]
    .value_counts()
    .rename_axis("production_status")
    .reset_index(name="number_of_sites")
)

print("\nRépartition selon la production :")
print(production_summary.to_string(index=False))


# ------------------------------------------------------------
# 6. Repérage des dossiers utiles pour les teneurs
# ------------------------------------------------------------

text_columns = [
    "production_notes",
    "reserves",
    "geologic_description",
    "workings_exploration",
]

for column in text_columns:
    df[column] = df[column].fillna("").astype(str)


combined_text = (
    df["production_notes"] + " " +
    df["reserves"] + " " +
    df["geologic_description"] + " " +
    df["workings_exploration"]
).str.lower()


# Expressions susceptibles de signaler une teneur ou un tonnage
grade_pattern = (
    r"\bgrade\b|"
    r"\bpercent\b|"
    r"\b%\s*sb\b|"
    r"\bsb\s*%\b|"
    r"\bppm\b|"
    r"\bounces?\b|"
    r"\boz\b|"
    r"\bg/t\b|"
    r"\btons?\b|"
    r"\btonnes?\b|"
    r"\bresource\b|"
    r"\breserve\b"
)

df["possible_grade_or_tonnage"] = combined_text.str.contains(
    grade_pattern,
    regex=True,
    na=False,
)


# ------------------------------------------------------------
# 7. Niveau de priorité documentaire
# ------------------------------------------------------------

def assign_review_priority(row):
    if (
        row["site_type_clean"] == "Mine"
        and row["production_clean"] == "Production reported"
        and row["possible_grade_or_tonnage"]
    ):
        return "Priority 1"

    if (
        row["site_type_clean"] in ["Mine", "Prospect"]
        and row["possible_grade_or_tonnage"]
    ):
        return "Priority 2"

    if row["possible_grade_or_tonnage"]:
        return "Priority 3"

    return "Low priority"


df["grade_review_priority"] = df.apply(
    assign_review_priority,
    axis=1,
)


# ------------------------------------------------------------
# 8. Exports
# ------------------------------------------------------------

site_type_summary.to_csv(
    OUTPUT_DIR / "summary_site_types.csv",
    index=False,
    encoding="utf-8-sig",
)

production_summary.to_csv(
    OUTPUT_DIR / "summary_production_status.csv",
    index=False,
    encoding="utf-8-sig",
)


columns_for_review = [
    "ARDF_number",
    "site",
    "latitude",
    "longitude_for_GIS",
    "site_type",
    "site_type_clean",
    "antimony_category",
    "production",
    "production_clean",
    "production_notes",
    "reserves",
    "commodities_main",
    "commodities_other",
    "ore_minerals",
    "geologic_description",
    "workings_exploration",
    "primary_reference",
    "references",
    "possible_grade_or_tonnage",
    "grade_review_priority",
]

grade_candidates = (
    df.loc[df["possible_grade_or_tonnage"], columns_for_review]
    .sort_values(
        by=["grade_review_priority", "site_type_clean", "site"]
    )
)

grade_candidates.to_csv(
    OUTPUT_DIR / "antimony_grade_candidates.csv",
    index=False,
    encoding="utf-8-sig",
)


# Base complète enrichie
df.to_csv(
    OUTPUT_DIR / "antimony_occurrences_analyzed.csv",
    index=False,
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 9. Résumé final
# ------------------------------------------------------------

print(
    "\nSites contenant potentiellement une teneur, "
    f"un tonnage ou une ressource : {len(grade_candidates):,}"
)

print("\nPriorités documentaires :")
print(df["grade_review_priority"].value_counts().to_string())

print("\nFichiers créés :")
print("- data_processed/summary_site_types.csv")
print("- data_processed/summary_production_status.csv")
print("- data_processed/antimony_grade_candidates.csv")
print("- data_processed/antimony_occurrences_analyzed.csv")