#!/usr/bin/env python3
"""State-level HPOP analysis using 2024 ACS 1-Year PUMS data."""
import pandas as pd
import numpy as np

from scripts.constants import (
    PUMS, Codes, Geo, OutputColumns, FileNames,
    ROOT, DATA_DIR, OUT_DIR
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

    # Add population counts
    df = merge_person_housing(person, housing, housing_cols=[
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.BLD,
    ])
    df = filter_housing_units(df)
    df = filter_adults(df)
    n_adults = df.groupby(PUMS.STATE).apply(
        lambda g: pd.Series({"n_adults": g[PUMS.PWGTP].sum()})
    ).reset_index()
    state = state.merge(n_adults, on=PUMS.STATE, how="left")

    hu = housing[housing[PUMS.TEN].notna()].copy()
    n_occ = hu.groupby(PUMS.STATE).apply(
        lambda g: pd.Series({"n_occupied_units": g[PUMS.WGTP].sum()})
    ).reset_index()
    state = state.merge(n_occ, on=PUMS.STATE, how="left")

    # Add rental-specific population counts
    df_rental = merge_person_housing(person, housing, housing_cols=[
        PUMS.TEN, PUMS.TYPEHUGQ,
    ])
    df_rental = filter_housing_units(df_rental)
    df_rental = filter_renters(df_rental)
    df_rental = filter_adults(df_rental)
    n_adults_rental = df_rental.groupby(PUMS.STATE).apply(
        lambda g: pd.Series({"n_adults_rental": g[PUMS.PWGTP].sum()})
    ).reset_index()
    state = state.merge(n_adults_rental, on=PUMS.STATE, how="left")

    hu_rental = housing[housing[PUMS.TEN] == Codes.RENTER_OCCUPIED].copy()
    n_rental_units = hu_rental.groupby(PUMS.STATE).apply(
        lambda g: pd.Series({"n_rental_units": g[PUMS.WGTP].sum()})
    ).reset_index()
    state = state.merge(n_rental_units, on=PUMS.STATE, how="left")

    # Add state abbreviations
    state = add_state_abbreviation(state)

    # Save
    save_output(state, FileNames.STATE_CSV, columns=OutputColumns.STATE_LEVEL)

    # ── Validation against Minneapolis Fed ──
    try:
        mfed = pd.read_excel(
            DATA_DIR / "mfed_hpop.xlsx", sheet_name="hpop_oown_state"
        )
        mfed = mfed[mfed["year"] == 2024].copy()
        mfed["state"] = mfed["fips"].map(Geo.FIPS_TO_STATE)
        mfed = mfed[mfed["state"].notna()].copy()

        merged = state.merge(
            mfed[["state", "hpop", "ownocc"]], on="state", suffixes=("_ours", "_mfed")
        )
        merged["delta_hpop"] = merged["hpop_ours"] - merged["hpop_mfed"]
        merged["delta_ownocc"] = merged["owner_occ_rate"] - merged["ownocc"]

        hpop_corr = merged["hpop_ours"].corr(merged["hpop_mfed"])
        hpop_mae = merged["delta_hpop"].abs().mean()
        ownocc_corr = merged["owner_occ_rate"].corr(merged["ownocc"])
        ownocc_mae = merged["delta_ownocc"].abs().mean()

        print("\n── Validation vs Minneapolis Fed ──")
        print(f"  HPOP:      r={hpop_corr:.4f}, MAE={hpop_mae:.2f}pp, bias={merged['delta_hpop'].mean():+.2f}pp")
        print(f"  Owner-Occ: r={ownocc_corr:.4f}, MAE={ownocc_mae:.2f}pp, bias={merged['delta_ownocc'].mean():+.2f}pp")
        print(f"  Mean HPOP: ours={merged['hpop_ours'].mean():.1f}% vs Fed={merged['hpop_mfed'].mean():.1f}%")
        print(f"  Mean OOR:  ours={merged['owner_occ_rate'].mean():.1f}% vs Fed={merged['ownocc'].mean():.1f}%")
    except Exception as e:
        print(f"\n── Fed validation skipped: {e} ──")

    # Print summary
    print()
    print(state[["state", "hpop", "owner_occ_rate", "gap_pp", "rent_to_income", "price_to_income"]]
          .sort_values("hpop", ascending=False).to_string(index=False))

    # National metrics (use same filter logic as compute_hpop_metrics)
    df = merge_person_housing(person, housing, housing_cols=[
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.BLD,
    ])
    df = filter_housing_units(df)
    df = filter_adults(df)
    df["owner_occ"] = df[PUMS.TEN].isin(Codes.OWNER_OCCUPIED)
    df["is_homeowner"] = df["owner_occ"] & df[PUMS.RELSHIPP].isin(Codes.HOMEOWNER_RELSHIPP)

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
