#!/usr/bin/env python
"""Toy analysis for Lab 1 (reproducible-setup).

Reads the patient roster in ``data/patients.csv`` and prints a small,
deterministic summary: cohort sizes, age distribution, and mean systolic
blood pressure by site. Also writes ``data/age_summary.csv`` so there is a
file artifact to diff between runs / machines / the container.

Run from the repo root:

    uv run python src/analysis.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "patients.csv"
OUT = ROOT / "data" / "age_summary.csv"


def main() -> None:
    print(f"pandas {pd.__version__}")

    df = pd.read_csv(DATA)
    print(f"loaded {len(df)} rows from {DATA.relative_to(ROOT).as_posix()}")

    print("\nage summary:")
    print(df["age"].describe().round(2).to_string())

    by_site = (
        df.groupby("site")
        .agg(n=("patient_id", "count"),
             mean_age=("age", "mean"),
             mean_systolic_bp=("systolic_bp", "mean"))
        .round(2)
        .sort_index()
    )
    print("\nby site:")
    print(by_site.to_string())

    by_cohort = (
        df.groupby("cohort")
        .agg(n=("patient_id", "count"), mean_age=("age", "mean"))
        .round(2)
        .sort_index()
    )
    print("\nby cohort:")
    print(by_cohort.to_string())

    by_site.to_csv(OUT)
    print(f"\nwrote {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
