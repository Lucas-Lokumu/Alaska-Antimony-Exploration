from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data_processed/agdb4_stream_sediment_sb.csv"
)

OUTPUT_FILE = Path(
    "data_processed/agdb4_stream_sediment_sb_extreme_values.csv"
)


df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
    low_memory=False,
)

df["sb_measured_ppm"] = pd.to_numeric(
    df["sb_measured_ppm"],
    errors="coerce",
)


# Valeurs mesurées uniquement
measured = df[
    df["sb_measured_ppm"].notna()
].copy()


# Classement décroissant
extreme_values = (
    measured.sort_values(
        "sb_measured_ppm",
        ascending=False,
    )
    .head(100)
)


columns_to_show = [
    "DDPD_ID",
    "AGDB_ID",
    "SPL_ID",
    "FIELD_ID",
    "LATITUDE",
    "LONGITUDE",
    "QUAD",
    "DISTRICT_NAME",
    "DEPOSIT_NAME",
    "MINE_NAME",
    "Sb_ppm",
    "Sb_AM",
    "Sb_ppm_ALL",
    "sb_measured_ppm",
    "sb_anomaly_class",
    "AGENCY",
]

columns_to_show = [
    column
    for column in columns_to_show
    if column in extreme_values.columns
]

extreme_values = extreme_values[
    columns_to_show
]


extreme_values.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


print("\n30 valeurs Sb les plus élevées :")

print(
    extreme_values
    .head(30)
    .to_string(index=False)
)

print(f"\nFichier créé : {OUTPUT_FILE}")