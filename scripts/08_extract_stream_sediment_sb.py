from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

DATA_DIR = Path("AGDB4_text/AGDB4_text")
OUTPUT_DIR = Path("data_processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GEOLOGY_FILE = DATA_DIR / "Geol_DeDuped.txt"
CHEMISTRY_FILE = DATA_DIR / "BV_P_Te.txt"

OUTPUT_FILE = OUTPUT_DIR / "agdb4_stream_sediment_sb.csv"
SUMMARY_FILE = OUTPUT_DIR / "summary_agdb4_stream_sediment_sb.csv"


# ------------------------------------------------------------
# 2. Colonnes utiles
# ------------------------------------------------------------

geology_columns = [
    "DDPD_ID",
    "DDPD_ID_text",
    "AGDB_ID",
    "SPL_ID",
    "FIELD_ID",
    "LATITUDE",
    "LONGITUDE",
    "SAMPLE_SOURCE",
    "PRIMARY_CLASS",
    "SECONDARY_CLASS",
    "SPECIFIC_NAME",
    "QUAD",
    "DISTRICT_NAME",
    "DEPOSIT_NAME",
    "MINE_NAME",
    "DATE_COLLECT",
    "AGENCY",
]

chemistry_columns = [
    "DDPD_ID",
    "Sb_ppm",
    "Sb_AM",
    "Sb_ppm_ALL",
]


# ------------------------------------------------------------
# 3. Lecture des données
# ------------------------------------------------------------

print("Lecture des informations géologiques...")

geology = pd.read_csv(
    GEOLOGY_FILE,
    sep=",",
    usecols=geology_columns,
    encoding="cp1252",
    low_memory=False,
)

print("Lecture des données Sb...")

chemistry = pd.read_csv(
    CHEMISTRY_FILE,
    sep=",",
    usecols=chemistry_columns,
    encoding="cp1252",
    low_memory=False,
)


# ------------------------------------------------------------
# 4. Nettoyage
# ------------------------------------------------------------

text_columns = [
    "SAMPLE_SOURCE",
    "PRIMARY_CLASS",
    "SECONDARY_CLASS",
    "SPECIFIC_NAME",
    "QUAD",
    "DISTRICT_NAME",
    "DEPOSIT_NAME",
    "MINE_NAME",
    "AGENCY",
    "Sb_AM",
    "Sb_ppm_ALL",
]

for column in text_columns:
    if column in geology.columns:
        geology[column] = (
            geology[column]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

for column in ["Sb_AM", "Sb_ppm_ALL"]:
    chemistry[column] = (
        chemistry[column]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

for column in ["LATITUDE", "LONGITUDE"]:
    geology[column] = pd.to_numeric(
        geology[column],
        errors="coerce",
    )

chemistry["Sb_ppm"] = pd.to_numeric(
    chemistry["Sb_ppm"],
    errors="coerce",
)


# ------------------------------------------------------------
# 5. Filtre sur les sédiments de ruisseau
# ------------------------------------------------------------

stream_sediments = geology[
    geology["SAMPLE_SOURCE"]
    .str.lower()
    .eq("stream")
    &
    geology["PRIMARY_CLASS"]
    .str.lower()
    .eq("sediment")
].copy()

print(
    f"Nombre de sédiments de ruisseau : "
    f"{len(stream_sediments):,}"
)


# ------------------------------------------------------------
# 6. Jointure avec Sb
# ------------------------------------------------------------

sb_stream = stream_sediments.merge(
    chemistry,
    on="DDPD_ID",
    how="left",
    validate="one_to_one",
)


# ------------------------------------------------------------
# 7. Interprétation des valeurs Sb
# ------------------------------------------------------------

def classify_sb_value(value):
    if pd.isna(value):
        return "No data"

    if value < 0:
        return "Below detection limit"

    if value == 0:
        return "Zero or coded value"

    return "Measured value"


sb_stream["sb_value_status"] = (
    sb_stream["Sb_ppm"]
    .apply(classify_sb_value)
)

# La valeur absolue d'une valeur négative représente
# généralement la limite de détection associée.

sb_stream["sb_detection_limit_ppm"] = (
    sb_stream["Sb_ppm"]
    .where(sb_stream["Sb_ppm"] < 0)
    .abs()
)

# Pour l'analyse quantitative, seules les valeurs positives
# sont conservées comme concentrations mesurées.

sb_stream["sb_measured_ppm"] = (
    sb_stream["Sb_ppm"]
    .where(sb_stream["Sb_ppm"] > 0)
)


# ------------------------------------------------------------
# 8. Contrôle des coordonnées
# ------------------------------------------------------------

valid_coordinates = (
    sb_stream["LATITUDE"].between(50, 72)
    & sb_stream["LONGITUDE"].between(-180, -125)
)

sb_stream["valid_alaska_coordinates"] = valid_coordinates

sb_stream = sb_stream[
    sb_stream["valid_alaska_coordinates"]
].copy()


# ------------------------------------------------------------
# 9. Statistiques descriptives
# ------------------------------------------------------------

measured = sb_stream[
    sb_stream["sb_measured_ppm"].notna()
].copy()

summary = pd.DataFrame(
    {
        "indicator": [
            "Total stream-sediment samples",
            "Samples with measured Sb",
            "Samples below detection limit",
            "Samples without Sb data",
            "Minimum measured Sb (ppm)",
            "Median measured Sb (ppm)",
            "Mean measured Sb (ppm)",
            "95th percentile Sb (ppm)",
            "98th percentile Sb (ppm)",
            "Maximum measured Sb (ppm)",
        ],
        "value": [
            len(sb_stream),
            measured["sb_measured_ppm"].notna().sum(),
            (
                sb_stream["sb_value_status"]
                == "Below detection limit"
            ).sum(),
            (
                sb_stream["sb_value_status"]
                == "No data"
            ).sum(),
            measured["sb_measured_ppm"].min(),
            measured["sb_measured_ppm"].median(),
            measured["sb_measured_ppm"].mean(),
            measured["sb_measured_ppm"].quantile(0.95),
            measured["sb_measured_ppm"].quantile(0.98),
            measured["sb_measured_ppm"].max(),
        ],
    }
)


# ------------------------------------------------------------
# 10. Classes géochimiques exploratoires
# ------------------------------------------------------------

if not measured.empty:
    threshold_90 = measured["sb_measured_ppm"].quantile(0.90)
    threshold_95 = measured["sb_measured_ppm"].quantile(0.95)
    threshold_98 = measured["sb_measured_ppm"].quantile(0.98)

    def classify_anomaly(value):
        if pd.isna(value):
            return "Not measured"

        if value >= threshold_98:
            return "Very high anomaly"

        if value >= threshold_95:
            return "High anomaly"

        if value >= threshold_90:
            return "Moderate anomaly"

        return "Background"

    sb_stream["sb_anomaly_class"] = (
        sb_stream["sb_measured_ppm"]
        .apply(classify_anomaly)
    )

else:
    sb_stream["sb_anomaly_class"] = "Not measured"


# ------------------------------------------------------------
# 11. Export
# ------------------------------------------------------------

sb_stream.to_csv(
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
# 12. Résultats
# ------------------------------------------------------------

print("\nStatistiques Sb :")
print(summary.to_string(index=False))

print("\nRépartition des classes géochimiques :")
print(
    sb_stream["sb_anomaly_class"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nFichiers créés :")
print(f"- {OUTPUT_FILE}")
print(f"- {SUMMARY_FILE}")