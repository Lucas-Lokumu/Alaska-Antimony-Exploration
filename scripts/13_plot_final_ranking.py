from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path(
    "data_processed/antimony_final_ranking.csv"
)

OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "final_antimony_ranking.png"


df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
)

df = df.sort_values(
    "final_score",
    ascending=True,
)


plt.figure(figsize=(10, 7))

plt.barh(
    df["site"],
    df["final_score"],
)

plt.xlabel("Final multicriteria score")
plt.ylabel("Antimony site")
plt.title("Final antimony exploration ranking in Alaska")

plt.xlim(
    0,
    df["final_score"].max() + 2,
)

for index, value in enumerate(df["final_score"]):
    plt.text(
        value + 0.2,
        index,
        f"{int(value)}",
        va="center",
        fontsize=9,
    )

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(f"Graphique créé : {OUTPUT_FILE}")