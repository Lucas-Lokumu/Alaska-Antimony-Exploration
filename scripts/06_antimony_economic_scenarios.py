from pathlib import Path

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# 1. Chemins
# ------------------------------------------------------------

INPUT_FILE = Path("data_processed/antimony_site_screening.csv")
OUTPUT_FILE = Path("data_processed/antimony_economic_scenarios.csv")


# ------------------------------------------------------------
# 2. Hypothèses économiques
# ------------------------------------------------------------
# Ces valeurs sont des hypothèses exploratoires.
# Elles ne constituent pas des estimations techniques de projet.

SCENARIOS = {
    "Low": {
        "antimony_price_usd_per_t": 44_754,
        "recovery_rate": 0.65,
        "payability_rate": 0.75,
        "mining_opex_usd_per_t_ore": 180,
        "processing_opex_usd_per_t_ore": 140,
        "transport_opex_usd_per_t_ore": 100,
        "initial_capex_usd": 25_000_000,
    },
    "Base": {
        "antimony_price_usd_per_t": 52_911,
        "recovery_rate": 0.75,
        "payability_rate": 0.80,
        "mining_opex_usd_per_t_ore": 140,
        "processing_opex_usd_per_t_ore": 110,
        "transport_opex_usd_per_t_ore": 75,
        "initial_capex_usd": 15_000_000,
    },
    "High": {
        "antimony_price_usd_per_t": 60_627,
        "recovery_rate": 0.85,
        "payability_rate": 0.85,
        "mining_opex_usd_per_t_ore": 110,
        "processing_opex_usd_per_t_ore": 85,
        "transport_opex_usd_per_t_ore": 50,
        "initial_capex_usd": 10_000_000,
    },
}


# ------------------------------------------------------------
# 3. Lecture de la base de présélection
# ------------------------------------------------------------

sites = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
)

text_columns = [
    "site_grade",
    "screening_priority",
    "tonnage_unit",
]

for column in text_columns:
    if column in sites.columns:
        sites[column] = (
            sites[column]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

numeric_columns = [
    "grade_mean_percent",
    "documented_tonnage",
]

for column in numeric_columns:
    sites[column] = pd.to_numeric(
        sites[column],
        errors="coerce",
    )


# ------------------------------------------------------------
# 4. Conversion exploratoire du tonnage
# ------------------------------------------------------------

def estimate_metric_tonnage(row):
    """
    Convertit le tonnage documenté en tonnes métriques.

    Hypothèses :
    - short tons : conversion explicite ;
    - kg : conversion explicite ;
    - tonnes métriques : valeur inchangée ;
    - 'ton' ou 'tons' : assimilés à des short tons uniquement
      dans ce modèle exploratoire.

    Cette dernière hypothèse devra être signalée dans le rapport.
    """

    tonnage = row["documented_tonnage"]

    if pd.isna(tonnage):
        return np.nan

    if pd.isna(row["tonnage_unit"]):
        return np.nan

    unit = str(row["tonnage_unit"]).strip().lower()

    if unit in [
        "short ton",
        "short tons",
        "ton",
        "tons",
    ]:
        return tonnage * 0.90718474

    if unit in [
        "tonne",
        "tonnes",
        "metric ton",
        "metric tons",
        "metric tonne",
        "metric tonnes",
    ]:
        return tonnage

    if unit in [
        "kg",
        "kilogram",
        "kilograms",
    ]:
        return tonnage / 1000

    return np.nan


sites["estimated_ore_tonnage_metric"] = sites.apply(
    estimate_metric_tonnage,
    axis=1,
)


# ------------------------------------------------------------
# 5. Calcul des scénarios
# ------------------------------------------------------------

results = []

for _, site in sites.iterrows():

    ore_tonnage = site["estimated_ore_tonnage_metric"]
    grade = site["grade_mean_percent"]

    for scenario_name, assumptions in SCENARIOS.items():

        price = assumptions["antimony_price_usd_per_t"]
        recovery_rate = assumptions["recovery_rate"]
        payability_rate = assumptions["payability_rate"]
        initial_capex = assumptions["initial_capex_usd"]

        opex_per_tonne_ore = (
            assumptions["mining_opex_usd_per_t_ore"]
            + assumptions["processing_opex_usd_per_t_ore"]
            + assumptions["transport_opex_usd_per_t_ore"]
        )

        if pd.isna(ore_tonnage) or pd.isna(grade):
            contained_sb = np.nan
            recovered_sb = np.nan
            payable_sb = np.nan
            gross_revenue = np.nan
            total_opex = np.nan
            operating_margin = np.nan
            pre_tax_project_margin = np.nan

        else:
            contained_sb = (
                ore_tonnage
                * grade
                / 100
            )

            recovered_sb = (
                contained_sb
                * recovery_rate
            )

            payable_sb = (
                recovered_sb
                * payability_rate
            )

            gross_revenue = (
                payable_sb
                * price
            )

            total_opex = (
                ore_tonnage
                * opex_per_tonne_ore
            )

            operating_margin = (
                gross_revenue
                - total_opex
            )

            pre_tax_project_margin = (
                operating_margin
                - initial_capex
            )

        results.append(
            {
                "site": site["site_grade"],
                "screening_priority": site["screening_priority"],
                "scenario": scenario_name,

                "grade_percent_sb": grade,
                "original_tonnage": site["documented_tonnage"],
                "original_tonnage_unit": site["tonnage_unit"],
                "estimated_ore_tonnage_metric": ore_tonnage,

                "antimony_price_usd_per_t": price,
                "recovery_rate": recovery_rate,
                "payability_rate": payability_rate,

                "mining_opex_usd_per_t_ore": assumptions[
                    "mining_opex_usd_per_t_ore"
                ],
                "processing_opex_usd_per_t_ore": assumptions[
                    "processing_opex_usd_per_t_ore"
                ],
                "transport_opex_usd_per_t_ore": assumptions[
                    "transport_opex_usd_per_t_ore"
                ],
                "total_opex_usd_per_t_ore": opex_per_tonne_ore,

                "contained_sb_metric_tonnes": contained_sb,
                "recovered_sb_metric_tonnes": recovered_sb,
                "payable_sb_metric_tonnes": payable_sb,

                "gross_revenue_usd": gross_revenue,
                "total_opex_usd": total_opex,
                "initial_capex_usd": initial_capex,
                "operating_margin_usd": operating_margin,
                "pre_tax_project_margin_usd": pre_tax_project_margin,
            }
        )


economic_results = pd.DataFrame(results)


# ------------------------------------------------------------
# 6. Prix d'équilibre
# ------------------------------------------------------------
# Prix minimum de l'antimoine payable nécessaire pour couvrir
# le CAPEX initial et l'OPEX total du scénario.

economic_results["break_even_price_usd_per_t_sb"] = np.where(
    economic_results["payable_sb_metric_tonnes"] > 0,
    (
        economic_results["total_opex_usd"]
        + economic_results["initial_capex_usd"]
    )
    / economic_results["payable_sb_metric_tonnes"],
    np.nan,
)


# Écart entre le prix du scénario et le prix d'équilibre.
# Une valeur positive indique une marge au-dessus du seuil.

economic_results["price_margin_percent"] = np.where(
    economic_results["antimony_price_usd_per_t"] > 0,
    (
        economic_results["antimony_price_usd_per_t"]
        - economic_results["break_even_price_usd_per_t_sb"]
    )
    / economic_results["antimony_price_usd_per_t"]
    * 100,
    np.nan,
)


# ------------------------------------------------------------
# 7. Classification indicative
# ------------------------------------------------------------

def classify_margin(row):
    margin = row["pre_tax_project_margin_usd"]

    if pd.isna(margin):
        return "Insufficient data"

    if margin > 0:
        return "Positive scenario margin"

    return "Negative scenario margin"


economic_results["economic_result"] = economic_results.apply(
    classify_margin,
    axis=1,
)


def classify_break_even(row):
    break_even = row["break_even_price_usd_per_t_sb"]
    market_price = row["antimony_price_usd_per_t"]

    if pd.isna(break_even):
        return "Insufficient data"

    if break_even <= market_price:
        return "Below scenario price"

    return "Above scenario price"


economic_results["break_even_status"] = economic_results.apply(
    classify_break_even,
    axis=1,
)


# ------------------------------------------------------------
# 8. Tri des résultats
# ------------------------------------------------------------

scenario_order = pd.CategoricalDtype(
    categories=["Low", "Base", "High"],
    ordered=True,
)

economic_results["scenario"] = economic_results[
    "scenario"
].astype(scenario_order)

economic_results = economic_results.sort_values(
    by=[
        "scenario",
        "pre_tax_project_margin_usd",
    ],
    ascending=[
        True,
        False,
    ],
)


# ------------------------------------------------------------
# 9. Export
# ------------------------------------------------------------

economic_results.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 10. Résultats du scénario central
# ------------------------------------------------------------

base_case = (
    economic_results[
        economic_results["scenario"] == "Base"
    ]
    .sort_values(
        by="pre_tax_project_margin_usd",
        ascending=False,
    )
)


print("\nScénario central :")

display_columns = [
    "site",
    "grade_percent_sb",
    "estimated_ore_tonnage_metric",
    "contained_sb_metric_tonnes",
    "payable_sb_metric_tonnes",
    "gross_revenue_usd",
    "total_opex_usd",
    "initial_capex_usd",
    "pre_tax_project_margin_usd",
    "break_even_price_usd_per_t_sb",
    "price_margin_percent",
    "economic_result",
]

print(
    base_case[
        display_columns
    ].to_string(
        index=False,
    )
)


# ------------------------------------------------------------
# 11. Résumé des résultats
# ------------------------------------------------------------

print("\nRépartition des résultats par scénario :")

scenario_summary = (
    economic_results.groupby(
        ["scenario", "economic_result"],
        observed=False,
    )
    .size()
    .reset_index(name="number_of_sites")
)

print(
    scenario_summary.to_string(
        index=False,
    )
)

print(f"\nFichier créé : {OUTPUT_FILE}")