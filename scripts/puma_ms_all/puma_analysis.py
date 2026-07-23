#!/usr/bin/env python3
"""PUMA-level HPOP analysis for Mississippi and NYC."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

from scripts.constants import (
    PUMS, Codes, Geo, OutputColumns, FileNames,
    ROOT, DATA_DIR, OUT_DIR, PUMA_OUT_DIR
)
from scripts.utils import (
    filter_housing_units, filter_adults, filter_owners,
    filter_renters, merge_person_housing,
    weighted_mean, compute_housing_form_shares,
    compute_hpop_metrics, save_output, load_pums_data,
)

PUMA_OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_puma_data(
    state_fips: int,
    puma_codes: Optional[List[str]] = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load PUMS data filtered to a specific state and optional PUMAs."""
    person, housing = load_pums_data(
        person_cols=PUMS.PUMA_PERSON_COLS,
        housing_cols=PUMS.PUMA_HOUSING_COLS,
    )

    person = person[person[PUMS.STATE] == state_fips].copy()
    housing = housing[housing[PUMS.STATE] == state_fips].copy()

    if puma_codes:
        person = person[person[PUMS.PUMA].isin(puma_codes)].copy()
        housing = housing[housing[PUMS.PUMA].isin(puma_codes)].copy()

    return person, housing


def get_puma_name(puma_code: int, region: str) -> str:
    if region == "NYC":
        return Geo.NYC_PUMA_NAMES.get(puma_code, f"PUMA {puma_code:05d}")
    elif region == "MS":
        return Geo.MS_PUMA_NAMES.get(f"{puma_code:05d}", f"PUMA {puma_code:05d}")
    return f"PUMA {puma_code:05d}"


def compute_puma_metrics(
    person: pd.DataFrame,
    housing: pd.DataFrame,
    state_fips: int,
    region_name: str = "",
) -> List[Dict[str, Any]]:
    """Compute HPOP and housing metrics for each PUMA."""
    results = []

    # Use the shared compute_hpop_metrics with PUMA as group_col
    grouped = compute_hpop_metrics(person, housing, group_col=PUMS.PUMA)

    # Also compute per-PUMA sample sizes and names
    hu = filter_housing_units(housing)
    hu_occ = hu[hu[PUMS.TEN].notna()].copy()

    df = merge_person_housing(person, housing, housing_cols=[
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.BLD, PUMS.GRNTP, PUMS.VALP, PUMS.WGTP,
    ])
    df = filter_housing_units(df)
    df["is_adult"] = df[PUMS.AGEP] >= Codes.ADULT_AGE
    adults = df[df["is_adult"]].copy()
    adults["owner_occ"] = adults[PUMS.TEN].isin(Codes.OWNER_OCCUPIED)

    pumas = sorted(grouped[PUMS.PUMA].unique())

    for puma in pumas:
        row = grouped[grouped[PUMS.PUMA] == puma].iloc[0]
        puma_adults = adults[adults[PUMS.PUMA] == puma]
        puma_hu_occ = hu_occ[hu_occ[PUMS.PUMA] == puma]

        n_adults = int(puma_adults[PUMS.PWGTP].sum())
        n_occupied = int(puma_hu_occ[PUMS.WGTP].sum())

        name = get_puma_name(int(puma), region_name)

        results.append({
            "state": int(state_fips),
            "puma": str(puma).zfill(5),
            "region": region_name,
            "name": name,
            "n_adults": n_adults,
            "n_occupied_units": n_occupied,
            "hpop": round(float(row["hpop"]), 4),
            "owner_occ_rate": round(float(row["owner_occ_rate"]), 4),
            "gap_pp": round(float(row["gap_pp"]), 4),
            "mean_rent": round(float(row["avg_annual_rent"]), 2) if pd.notna(row.get("avg_annual_rent")) else np.nan,
            "mean_rent_18_64": round(float(row["avg_annual_rent_18_64"]), 2) if pd.notna(row.get("avg_annual_rent_18_64")) else np.nan,
            "rent_to_income": round(float(row["rent_to_income"] * 100), 2) if pd.notna(row.get("rent_to_income")) else np.nan,
            "rent_to_income_18_64": round(float(row["rent_to_income_18_64"] * 100), 2) if pd.notna(row.get("rent_to_income_18_64")) else np.nan,
            "mean_adult_income": round(float(row["avg_adult_income"]), 2) if pd.notna(row.get("avg_adult_income")) else np.nan,
            "sf_detached_share": round(float(row.get("sf_detached", 0)), 2),
            "multifamily_share": round(float(row.get("pct_multifamily", 0)), 2),
        })

    return results


def main():
    print("=" * 60)
    print("PUMA-LEVEL HPOP ANALYSIS: Mississippi & NYC")
    print("=" * 60)

    # ── Mississippi ──
    print(f"\nLoading PUMS data for Mississippi (FIPS={Geo.MS_STATE_FIPS})...")
    ms_person, ms_housing = load_puma_data(Geo.MS_STATE_FIPS)
    print(f"  Person records: {len(ms_person):,}")
    print(f"  Housing records: {len(ms_housing):,}")

    print("Computing Mississippi PUMA metrics...")
    ms_results = compute_puma_metrics(ms_person, ms_housing, Geo.MS_STATE_FIPS, "MS")
    ms_df = pd.DataFrame(ms_results)
    save_output(ms_df, FileNames.MS_PUMA_CSV, columns=OutputColumns.PUMA_LEVEL, output_dir=PUMA_OUT_DIR)
    print(f"Saved {len(ms_df)} Mississippi PUMAs")

    # ── NYC ──
    print(f"\nLoading PUMS data for NYC (FIPS={Geo.NY_STATE_FIPS})...")
    nyc_person, nyc_housing = load_puma_data(Geo.NY_STATE_FIPS, list(Geo.NYC_PUMAS))
    print(f"  Person records: {len(nyc_person):,}")
    print(f"  Housing records: {len(nyc_housing):,}")

    print("Computing NYC PUMA metrics...")
    nyc_results = compute_puma_metrics(nyc_person, nyc_housing, Geo.NY_STATE_FIPS, "NYC")
    nyc_df = pd.DataFrame(nyc_results)
    save_output(nyc_df, FileNames.NYC_PUMA_CSV, columns=OutputColumns.PUMA_LEVEL, output_dir=PUMA_OUT_DIR)
    print(f"Saved {len(nyc_df)} NYC PUMAs")

    print("\n" + "=" * 60)
    print("SUMMARY: Mississippi PUMAs")
    print("=" * 60)
    cols = ["puma", "name", "hpop", "owner_occ_rate", "gap_pp", "multifamily_share", "sf_detached_share", "rent_to_income"]
    print(ms_df[cols].sort_values("gap_pp").to_string(index=False))

    print("\n" + "=" * 60)
    print("SUMMARY: NYC PUMAs")
    print("=" * 60)
    print(nyc_df[cols].sort_values("gap_pp").to_string(index=False))

    return ms_df, nyc_df


if __name__ == "__main__":
    main()
