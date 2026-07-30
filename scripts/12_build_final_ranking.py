from pathlib import Path

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

INPUT_FILE = Path(
    "data_processed/antimony_sites_geology.csv"
)

OUTPUT_FILE = Path(
    "data_processed/antimony_final_ranking.csv"
)

SUMMARY_FILE = Path(
    "data_processed/summary_antimony_final_ranking.csv"
)


# ------------------------------------------------------------
# 2. Lecture
# ------------------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
    low_memory=False,
)

print(f"Nombre de sites chargés : {len(df)}")


# ------------------------------------------------------------
# 3. Renommage des champs tronqués par le Shapefile
# ------------------------------------------------------------

column_mapping = {
    "screening_": "screening_priority",
    "screenin_1": "screening_score",
    "grade_mean": "grade_mean_percent",
    "documented": "documented_tonnage",
    "tonnage_un": "tonnage_unit",
    "geochemica": "geochemical_score",
    "geochemi_1": "geochemical_support",
    "GROUP_LA_1": "geologic_unit_code",
    "GROUP_NAME": "geologic_unit_name",
    "GROUP_AGE": "geologic_age",
}

df = df.rename(columns=column_mapping)


# ------------------------------------------------------------
# 4. Vérification des colonnes obligatoires
# ------------------------------------------------------------

required_columns = [
    "site",
    "screening_priority",
    "screening_score",
    "geochemical_score",
    "geochemical_support",
    "geologic_unit_code",
    "geologic_unit_name",
    "geologic_age",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise KeyError(
        "Colonnes manquantes dans le CSV : "
        + ", ".join(missing_columns)
    )


# ------------------------------------------------------------
# 5. Nettoyage des textes
# ------------------------------------------------------------

text_columns = [
    "site",
    "screening_priority",
    "tonnage_unit",
    "geochemical_support",
    "geologic_unit_code",
    "geologic_unit_name",
    "geologic_age",
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
# 6. Nettoyage numérique
# ------------------------------------------------------------

numeric_columns = [
    "screening_score",
    "geochemical_score",
    "grade_mean_percent",
    "documented_tonnage",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )


# ------------------------------------------------------------
# 7. Score final
# ------------------------------------------------------------
# Le contexte géologique n'est pas transformé en points,
# car aucune pondération scientifique robuste n'a encore
# été définie pour les unités géologiques.

df["final_score"] = (
    df["screening_score"].fillna(0)
    + df["geochemical_score"].fillna(0)
)


# ------------------------------------------------------------
# 8. Priorité finale
# ------------------------------------------------------------

def classify_final_priority(score):
    if pd.isna(score):
        return "Insufficient data"

    if score >= 20:
        return "High final priority"

    if score >= 14:
        return "Medium final priority"

    return "Low final priority"


df["final_priority"] = (
    df["final_score"]
    .apply(classify_final_priority)
)


# ------------------------------------------------------------
# 9. Complétude des données
# ------------------------------------------------------------

def classify_data_completeness(row):
    has_grade = pd.notna(
        row.get("grade_mean_percent")
    )

    has_tonnage = pd.notna(
        row.get("documented_tonnage")
    )

    has_geology = (
        pd.notna(row.get("geologic_unit_name"))
        and str(
            row.get("geologic_unit_name")
        ).strip() != ""
    )

    if has_grade and has_tonnage and has_geology:
        return "Complete screening data"

    if has_grade and has_geology:
        return "Grade and geology available"

    if has_geology:
        return "Geology available only"

    return "Incomplete data"


df["data_completeness"] = df.apply(
    classify_data_completeness,
    axis=1,
)


# ------------------------------------------------------------
# 10. Indicateur géologique descriptif
# ------------------------------------------------------------
# Cet indicateur ne modifie pas le score.
# Il facilite seulement l'interprétation du classement.

def classify_geologic_context(row):
    text = " ".join(
        [
            str(row.get("geologic_unit_name", "")),
            str(row.get("geologic_age", "")),
        ]
    ).lower()

    if any(
        keyword in text
        for keyword in [
            "schist",
            "phyllite",
            "metasediment",
            "metamorphic",
        ]
    ):
        return "Metamorphic or metasedimentary context"

    if any(
        keyword in text
        for keyword in [
            "volcanic",
            "andesite",
            "basalt",
            "volcaniclastic",
        ]
    ):
        return "Volcanic context"

    if any(
        keyword in text
        for keyword in [
            "granite",
            "granitic",
            "plutonic",
            "intrusive",
        ]
    ):
        return "Intrusive context"

    if any(
        keyword in text
        for keyword in [
            "sedimentary",
            "limestone",
            "sandstone",
            "shale",
        ]
    ):
        return "Sedimentary context"

    return "Other or mixed context"


df["geologic_context"] = df.apply(
    classify_geologic_context,
    axis=1,
)


# ------------------------------------------------------------
# 11. Tri et rang
# ------------------------------------------------------------

priority_order = pd.CategoricalDtype(
    categories=[
        "High final priority",
        "Medium final priority",
        "Low final priority",
        "Insufficient data",
    ],
    ordered=True,
)

df["final_priority"] = df[
    "final_priority"
].astype(priority_order)

df = df.sort_values(
    by=[
        "final_score",
        "screening_score",
        "geochemical_score",
        "grade_mean_percent",
    ],
    ascending=[
        False,
        False,
        False,
        False,
    ],
    na_position="last",
).reset_index(drop=True)

df["final_rank"] = (
    np.arange(1, len(df) + 1)
)


# ------------------------------------------------------------
# 12. Organisation des colonnes
# ------------------------------------------------------------

preferred_columns = [
    "final_rank",
    "site",
    "final_score",
    "final_priority",

    "screening_score",
    "screening_priority",

    "geochemical_score",
    "geochemical_support",

    "grade_mean_percent",
    "documented_tonnage",
    "tonnage_unit",

    "geologic_unit_code",
    "geologic_unit_name",
    "geologic_age",
    "geologic_context",

    "data_completeness",
]

existing_preferred_columns = [
    column
    for column in preferred_columns
    if column in df.columns
]

remaining_columns = [
    column
    for column in df.columns
    if column not in existing_preferred_columns
]

df = df[
    existing_preferred_columns
    + remaining_columns
]


# ------------------------------------------------------------
# 13. Résumé par priorité
# ------------------------------------------------------------

summary = (
    df.groupby(
        "final_priority",
        observed=False,
    )
    .agg(
        number_of_sites=("site", "size"),
        mean_final_score=("final_score", "mean"),
        mean_screening_score=(
            "screening_score",
            "mean",
        ),
        mean_geochemical_score=(
            "geochemical_score",
            "mean",
        ),
        mean_grade_percent=(
            "grade_mean_percent",
            "mean",
        ),
    )
    .reset_index()
)


# ------------------------------------------------------------
# 14. Exports
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)

summary.to_csv(
    SUMMARY_FILE,
    index=False,
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 15. Affichage
# ------------------------------------------------------------

print("\nClassement final :")

display_columns = [
    "final_rank",
    "site",
    "final_score",
    "final_priority",
    "screening_score",
    "geochemical_score",
    "grade_mean_percent",
    "documented_tonnage",
    "tonnage_unit",
    "geologic_unit_code",
    "geologic_context",
]

print(
    df[
        display_columns
    ].to_string(
        index=False,
    )
)

print("\nRésumé par priorité finale :")
print(
    summary.to_string(
        index=False,
    )
)

print("\nFichiers créés :")
print(f"- {OUTPUT_FILE}")
print(f"- {SUMMARY_FILE}")