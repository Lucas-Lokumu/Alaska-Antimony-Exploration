from pathlib import Path
import pandas as pd


# -------------------------------------------------------------------
# 1. Chemins
# -------------------------------------------------------------------

INPUT_FILE = Path("geology_ARDF_csv/ardfcomp.csv")
OUTPUT_DIR = Path("data_processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# 2. Lecture du fichier
# -------------------------------------------------------------------

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Nombre total de sites : {len(df):,}")
print(f"Nombre de colonnes : {len(df.columns)}")


# -------------------------------------------------------------------
# 3. Fonctions de recherche
# -------------------------------------------------------------------

def contains_commodity(series: pd.Series, symbol: str) -> pd.Series:
    """
    Recherche un symbole chimique comme élément indépendant
    dans une liste séparée par des virgules.

    Exemple :
    'Ag, As, Sb, Zn' -> correspond à Sb
    """
    pattern = rf"(?i)(?:^|,\s*){symbol}\??(?:\s*,|$)"
    return series.fillna("").astype(str).str.contains(pattern, regex=True)


def contains_stibnite(series: pd.Series) -> pd.Series:
    """
    Recherche la stibine dans la colonne des minéraux métalliques.
    """
    return (
        series.fillna("")
        .astype(str)
        .str.contains(r"(?i)\bstibnite\??\b", regex=True)
    )


# -------------------------------------------------------------------
# 4. Filtres antimoine
# -------------------------------------------------------------------

mask_sb_main = contains_commodity(df["commodities_main"], "Sb")
mask_sb_other = contains_commodity(df["commodities_other"], "Sb")
mask_stibnite = contains_stibnite(df["ore_minerals"])

mask_antimony_all = mask_sb_main | mask_sb_other | mask_stibnite


# -------------------------------------------------------------------
# 5. Création d'une catégorie de priorité
# -------------------------------------------------------------------

df_antimony = df.loc[mask_antimony_all].copy()

df_antimony["antimony_category"] = "Stibnite mentioned only"

df_antimony.loc[
    mask_sb_other.loc[df_antimony.index],
    "antimony_category"
] = "Secondary commodity"

df_antimony.loc[
    mask_sb_main.loc[df_antimony.index],
    "antimony_category"
] = "Main commodity"


# Indicateurs binaires utiles pour les analyses suivantes
df_antimony["sb_main"] = mask_sb_main.loc[df_antimony.index].astype(int)
df_antimony["sb_other"] = mask_sb_other.loc[df_antimony.index].astype(int)
df_antimony["stibnite_present"] = (
    mask_stibnite.loc[df_antimony.index].astype(int)
)


# -------------------------------------------------------------------
# 6. Sélection et ordre des colonnes
# -------------------------------------------------------------------

columns_to_keep = [
    "ARDF_number",
    "site",
    "site_type",
    "site_status",
    "latitude",
    "longitude",
    "longitude_for_GIS",
    "quad_250",
    "quad_63360",
    "commodities_main",
    "commodities_other",
    "ore_minerals",
    "gangue_minerals",
    "production",
    "production_notes",
    "reserves",
    "generic_deposit_model",
    "deposit_model",
    "deposit_model_number",
    "geologic_description",
    "workings_exploration",
    "alteration",
    "age",
    "primary_reference",
    "references",
    "last_report_date",
    "antimony_category",
    "sb_main",
    "sb_other",
    "stibnite_present",
]

df_antimony = df_antimony[columns_to_keep]


# -------------------------------------------------------------------
# 7. Export
# -------------------------------------------------------------------

output_file = OUTPUT_DIR / "antimony_occurrences_ardf.csv"

df_antimony.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


# -------------------------------------------------------------------
# 8. Résumé
# -------------------------------------------------------------------

print("\nRésultats du filtrage :")
print(f"Sb comme substance principale : {mask_sb_main.sum():,}")
print(f"Sb comme substance secondaire : {mask_sb_other.sum():,}")
print(f"Stibine mentionnée : {mask_stibnite.sum():,}")
print(f"Sites distincts retenus : {len(df_antimony):,}")

print("\nRépartition finale :")
print(df_antimony["antimony_category"].value_counts())

print(f"\nFichier créé : {output_file}")