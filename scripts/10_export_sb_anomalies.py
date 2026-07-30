from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data_processed/agdb4_stream_sediment_sb.csv"
)

OUTPUT_FILE = Path(
    "data_processed/agdb4_stream_sediment_sb_anomalies.csv"
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


# Conserver uniquement les anomalies modérées à très fortes
anomalies = df[
    df["sb_anomaly_class"].isin(
        [
            "Moderate anomaly",
            "High anomaly",
            "Very high anomaly",
        ]
    )
].copy()


# Valeur cartographique plafonnée pour éviter
# qu'un maximum extrême écrase toute la palette.
anomalies["sb_ppm_map"] = (
    anomalies["sb_measured_ppm"]
    .clip(upper=5000)
)


# Indicateur des valeurs supérieures au plafond
anomalies["above_map_cap"] = (
    anomalies["sb_measured_ppm"] > 5000
)


# Tri décroissant
anomalies = anomalies.sort_values(
    "sb_measured_ppm",
    ascending=False,
)


anomalies.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


print(f"Nombre d'anomalies exportées : {len(anomalies):,}")

print("\nRépartition :")
print(
    anomalies["sb_anomaly_class"]
    .value_counts()
    .to_string()
)

print(
    "\nValeurs supérieures au plafond cartographique "
    f"de 5 000 ppm : {anomalies['above_map_cap'].sum()}"
)

print(f"\nFichier créé : {OUTPUT_FILE}")
