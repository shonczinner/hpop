#!/usr/bin/env python3
"""State-level HPOP analysis using 2024 ACS 1-Year PUMS data."""
import pandas as pd
import numpy as np

from scripts.constants import (
    PUMS, Codes, Geo, OutputColumns, FileNames,
    DATA_DIR, OUT_DIR
)
from scripts.utils import (
    load_pums_data,
    filter_housing_units,
    filter_adults,
    filter_owners,
    filter_renters,
    merge_person_housing,
    weighted_mean,
    add_state_abbreviation,
    compute_rent_to_income,
    compute_hpop_metrics,
    save_output,
)


def main() -> pd.DataFrame:
    print("Loading PUMS data...")
    person, housing = load_pums_data()
    housing = filter_housing_units(housing)

    print("Computing state-level metrics...")
    state = compute_hpop_metrics(person, housing, group_col=PUMS.STATE)

    # Exclude Puerto Rico
    state = state[state[PUMS.STATE] != Geo.PR_FIPS].copy()

    # Add state abbreviations
    state = add_state_abbreviation(state)

    # Save
    save_output(state, FileNames.STATE_CSV, columns=OutputColumns.STATE_LEVEL)

    # Print summary
    print(state[["state", "hpop", "owner_occ_rate", "gap_pp", "rent_to_income", "price_to_income"]]
          .sort_values("hpop", ascending=False).to_string(index=False))

    # National metrics (use same filter logic as compute_hpop_metrics)
    df = merge_person_housing(person, housing, housing_cols=[
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.BLD,
    ])
    df = filter_housing_units(df)
    df = filter_adults(df)
    df["owner_occ"] = df[PUMS.TEN].isin(Codes.OWNER_OCCUPIED)
    df["is_homeowner"] = df["owner_occ"] & df[PUMS.RELSHIPP].isin(Codes.HOUSEHOLDER_SPOUSE_PARTNER)

    hu = housing[housing[PUMS.TEN].notna()].copy()
    hu["owner_occ"] = hu[PUMS.TEN].isin(Codes.OWNER_OCCUPIED)

    renters = merge_person_housing(person, housing, housing_cols=[
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.GRNTP,
    ])
    renters = filter_housing_units(renters)
    renters = filter_renters(renters)
    renters = filter_adults(renters)
    renters = renters[
        renters[PUMS.GRNTP].notna() &
        (renters[PUMS.GRNTP] > 0) &
        renters[PUMS.PINCP].notna()
    ].copy()
    renters["annual_rent"] = renters[PUMS.GRNTP] * 12

    nat_hpop = weighted_mean(df, "is_homeowner") * 100
    nat_ownocc = (hu[PUMS.WGTP] * hu["owner_occ"]).sum() / hu[PUMS.WGTP].sum() * 100
    nat_rent = compute_rent_to_income(renters, "annual_rent", PUMS.PINCP)
    print(f"\nNational HPOP: {nat_hpop:.1f}%")
    print(f"National Owner-Occ: {nat_ownocc:.1f}%")
    print(f"National Gap: {nat_hpop - nat_ownocc:.1f} pp")
    print(f"National Rent-to-Income: {nat_rent:.3f}")

    return state


if __name__ == "__main__":
    main()
