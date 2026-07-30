from pathlib import Path
from math import asin, cos, radians, sin, sqrt

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

SITES_FILE = Path(
    "data_processed/antimony_site_screening.csv"
)

ANOMALIES_FILE = Path(
    "data_processed/agdb4_stream_sediment_sb_anomalies.csv"
)

OUTPUT_FILE = Path(
    "data_processed/antimony_sites_sb_anomaly_proximity.csv"
)


# ------------------------------------------------------------
# 2. Lecture
# ------------------------------------------------------------

sites = pd.read_csv(
    SITES_FILE,
    encoding="utf-8-sig",
)

anomalies = pd.read_csv(
    ANOMALIES_FILE,
    encoding="utf-8-sig",
    low_memory=False,
)


# ------------------------------------------------------------
# 3. Nettoyage numérique
# ------------------------------------------------------------

site_numeric_columns = [
    "latitude",
    "longitude_for_GIS",
    "grade_mean_percent",
    "documented_tonnage",
    "screening_score",
]

for column in site_numeric_columns:
    if column in sites.columns:
        sites[column] = pd.to_numeric(
            sites[column],
            errors="coerce",
        )

anomaly_numeric_columns = [
    "LATITUDE",
    "LONGITUDE",
    "sb_measured_ppm",
]

for column in anomaly_numeric_columns:
    anomalies[column] = pd.to_numeric(
        anomalies[column],
        errors="coerce",
    )


sites = sites.dropna(
    subset=[
        "latitude",
        "longitude_for_GIS",
    ]
).copy()

anomalies = anomalies.dropna(
    subset=[
        "LATITUDE",
        "LONGITUDE",
        "sb_measured_ppm",
    ]
).copy()


# ------------------------------------------------------------
# 4. Distance de Haversine
# ------------------------------------------------------------

def haversine_km(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2,
):
    """
    Distance entre deux coordonnées géographiques en kilomètres.
    """

    earth_radius_km = 6371.0088

    lat1 = radians(latitude_1)
    lon1 = radians(longitude_1)
    lat2 = radians(latitude_2)
    lon2 = radians(longitude_2)

    delta_latitude = lat2 - lat1
    delta_longitude = lon2 - lon1

    value = (
        sin(delta_latitude / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_longitude / 2) ** 2
    )

    return (
        2
        * earth_radius_km
        * asin(sqrt(value))
    )


# ------------------------------------------------------------
# 5. Analyse de proximité
# ------------------------------------------------------------

results = []

for _, site in sites.iterrows():

    site_latitude = site["latitude"]
    site_longitude = site["longitude_for_GIS"]

    distances = anomalies.apply(
        lambda row: haversine_km(
            site_latitude,
            site_longitude,
            row["LATITUDE"],
            row["LONGITUDE"],
        ),
        axis=1,
    )

    local_anomalies = anomalies.copy()
    local_anomalies["distance_km"] = distances

    nearest_index = (
        local_anomalies["distance_km"]
        .idxmin()
    )

    nearest = local_anomalies.loc[
        nearest_index
    ]

    within_10_km = local_anomalies[
        local_anomalies["distance_km"] <= 10
    ]

    within_25_km = local_anomalies[
        local_anomalies["distance_km"] <= 25
    ]

    within_50_km = local_anomalies[
        local_anomalies["distance_km"] <= 50
    ]

    very_high_25_km = within_25_km[
        within_25_km["sb_anomaly_class"]
        == "Very high anomaly"
    ]

    high_or_very_high_25_km = within_25_km[
        within_25_km["sb_anomaly_class"].isin(
            [
                "High anomaly",
                "Very high anomaly",
            ]
        )
    ]

    maximum_sb_25_km = (
        within_25_km["sb_measured_ppm"].max()
        if not within_25_km.empty
        else np.nan
    )

    results.append(
        {
            "site": site["site_grade"],
            "screening_priority": site[
                "screening_priority"
            ],
            "screening_score": site[
                "screening_score"
            ],
            "grade_mean_percent": site[
                "grade_mean_percent"
            ],
            "documented_tonnage": site[
                "documented_tonnage"
            ],
            "tonnage_unit": site[
                "tonnage_unit"
            ],
            "latitude": site_latitude,
            "longitude_for_GIS": site_longitude,

            "nearest_anomaly_distance_km": nearest[
                "distance_km"
            ],
            "nearest_anomaly_sb_ppm": nearest[
                "sb_measured_ppm"
            ],
            "nearest_anomaly_class": nearest[
                "sb_anomaly_class"
            ],

            "anomalies_within_10_km": len(
                within_10_km
            ),
            "anomalies_within_25_km": len(
                within_25_km
            ),
            "anomalies_within_50_km": len(
                within_50_km
            ),

            "high_or_very_high_within_25_km": len(
                high_or_very_high_25_km
            ),
            "very_high_within_25_km": len(
                very_high_25_km
            ),
            "maximum_sb_within_25_km_ppm": (
                maximum_sb_25_km
            ),
        }
    )


proximity = pd.DataFrame(results)


# ------------------------------------------------------------
# 6. Score géochimique
# ------------------------------------------------------------

def geochemical_score(row):
    score = 0

    distance = row["nearest_anomaly_distance_km"]

    if distance <= 0.5:
        score += 4
    elif distance <= 2:
        score += 3
    elif distance <= 5:
        score += 2
    elif distance <= 10:
        score += 1

    very_high_count = row["very_high_within_25_km"]

    if very_high_count >= 30:
        score += 4
    elif very_high_count >= 15:
        score += 3
    elif very_high_count >= 5:
        score += 2
    elif very_high_count >= 1:
        score += 1

    maximum_sb = row["maximum_sb_within_25_km_ppm"]

    if maximum_sb >= 5000:
        score += 3
    elif maximum_sb >= 1000:
        score += 2
    elif maximum_sb >= 200:
        score += 1

    return score


proximity["geochemical_score"] = proximity.apply(
    geochemical_score,
    axis=1,
)


def geochemical_priority(score):
    if score >= 9:
        return "Strong geochemical support"

    if score >= 6:
        return "Moderate geochemical support"

    return "Limited geochemical support"


proximity["geochemical_support"] = (
    proximity["geochemical_score"]
    .apply(geochemical_priority)
)

# ------------------------------------------------------------
# 7. Tri et export
# ------------------------------------------------------------

proximity = proximity.sort_values(
    by=[
        "geochemical_score",
        "screening_score",
    ],
    ascending=[
        False,
        False,
    ],
)

proximity.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 8. Résultats
# ------------------------------------------------------------

print(
    f"Nombre de sites analysés : "
    f"{len(proximity)}"
)

print("\nProximité des anomalies Sb :")

print(
    proximity[
        [
            "site",
            "screening_priority",
            "nearest_anomaly_distance_km",
            "nearest_anomaly_sb_ppm",
            "anomalies_within_25_km",
            "very_high_within_25_km",
            "maximum_sb_within_25_km_ppm",
            "geochemical_score",
            "geochemical_support",
        ]
    ]
    .to_string(index=False)
)

print(f"\nFichier créé : {OUTPUT_FILE}")