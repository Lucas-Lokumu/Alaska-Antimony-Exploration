from pathlib import Path

import pandas as pd


DATA_DIR = Path("AGDB4_text/AGDB4_text")

FILES_TO_INSPECT = [
    "Geol_DeDuped",
    "BV_P_Te",
    "Parameter",
    "DataDictionary",
]


def find_file(stem: str) -> Path:
    """Recherche un fichier même si Windows masque son extension."""
    matches = list(DATA_DIR.glob(f"{stem}.*"))

    if not matches:
        raise FileNotFoundError(
            f"Fichier introuvable pour : {stem}"
        )

    return matches[0]


for stem in FILES_TO_INSPECT:
    file_path = find_file(stem)

    print("\n" + "=" * 70)
    print(f"Fichier : {file_path.name}")

    # sep=None permet à pandas de détecter le séparateur.
    preview = pd.read_csv(
        file_path,
        sep=None,
        engine="python",
        nrows=5,
        encoding="utf-8-sig",
    )

    print(f"Nombre de colonnes : {len(preview.columns)}")
    print("Colonnes :")
    print(preview.columns.tolist())

    print("\nAperçu :")
    print(preview.head().to_string(index=False))