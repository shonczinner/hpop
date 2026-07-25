#!/usr/bin/env python3
"""Shared utilities for data loading, filtering, and computation."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any

from scripts.constants import (
    PUMS, Codes, Geo, OutputColumns, FileNames,
    ROOT, DATA_DIR, OUT_DIR
)


# Ensure output directory exists
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_pums_data(
    person_cols: Optional[List[str]] = None,
    housing_cols: Optional[List[str]] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and concatenate PUMS person and housing data (a + b splits).

    Args:
        person_cols: Columns to load from person files. Defaults to core columns.
        housing_cols: Columns to load from housing files. Defaults to core columns.

    Returns:
        Tuple of (person_df, housing_df)
    """
    person_cols = person_cols or PUMS.PERSON_COLS
    housing_cols = housing_cols or PUMS.HOUSING_COLS

    person = pd.concat([
        pd.read_csv(DATA_DIR / "psam_pusa.csv", usecols=person_cols, dtype={PUMS.SERIALNO: str}),
        pd.read_csv(DATA_DIR / "psam_pusb.csv", usecols=person_cols, dtype={PUMS.SERIALNO: str}),
    ], ignore_index=True)

    housing = pd.concat([
        pd.read_csv(DATA_DIR / "psam_husa.csv", usecols=housing_cols, dtype={PUMS.SERIALNO: str}),
        pd.read_csv(DATA_DIR / "psam_husb.csv", usecols=housing_cols, dtype={PUMS.SERIALNO: str}),
    ], ignore_index=True)

    return person, housing


def filter_housing_units(df: pd.DataFrame, type_col: str = PUMS.TYPEHUGQ) -> pd.DataFrame:
    """Filter to housing units (TYPEHUGQ == 1)."""
    return df[df[type_col] == Codes.HOUSING_UNIT].copy()


def filter_adults(df: pd.DataFrame, age_col: str = PUMS.AGEP, min_age: int = Codes.ADULT_AGE) -> pd.DataFrame:
    """Filter to adults (age >= 18 by default)."""
    return df[df[age_col] >= min_age].copy()


def filter_owners(
    df: pd.DataFrame,
    ten_col: str = PUMS.TEN,
    rel_col: str = PUMS.RELSHIPP,
) -> pd.DataFrame:
    """Filter to owner-occupiers (householder/spouse/partner in owner-occupied unit)."""
    return df[
        df[ten_col].isin(Codes.OWNER_OCCUPIED) &
        df[rel_col].isin(Codes.HOMEOWNER_RELSHIPP)
    ].copy()


def filter_renters(df: pd.DataFrame, ten_col: str = PUMS.TEN) -> pd.DataFrame:
    """Filter to renters (TEN == 3)."""
    return df[df[ten_col] == Codes.RENTER_OCCUPIED].copy()


def merge_person_housing(
    person: pd.DataFrame,
    housing: pd.DataFrame,
    housing_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Merge person and housing data on SERIALNO + STATE.

    Args:
        person: Person-level DataFrame
        housing: Housing-level DataFrame
        housing_cols: Columns to bring from housing. Defaults to all housing cols.

    Returns:
        Merged DataFrame
    """
    housing_cols = housing_cols or [
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.BLD, PUMS.GRNTP, PUMS.VALP, PUMS.WGTP,
    ]
    return person.merge(
        housing[housing_cols + [PUMS.SERIALNO, PUMS.STATE]],
        on=[PUMS.SERIALNO, PUMS.STATE],
        how="left",
    )


def weighted_mean(
    df: pd.DataFrame,
    value_col: str,
    weight_col: str = PUMS.PWGTP,
) -> float:
    """Compute weighted mean of value_col using weight_col."""
    w = df[weight_col]
    return (w * df[value_col]).sum() / w.sum()


def weighted_median(
    df: pd.DataFrame,
    value_col: str,
    weight_col: str = PUMS.PWGTP,
) -> float:
    """Compute weighted median of value_col using weight_col."""
    df = df.dropna(subset=[value_col, weight_col])
    if len(df) == 0:
        return np.nan
    sorted_idx = df[value_col].argsort()
    sorted_values = df[value_col].iloc[sorted_idx].values
    sorted_weights = df[weight_col].iloc[sorted_idx].values
    cumsum = np.cumsum(sorted_weights)
    cutoff = cumsum[-1] / 2.0
    idx = np.searchsorted(cumsum, cutoff)
    return float(sorted_values[min(idx, len(sorted_values) - 1)])


def weighted_sum(
    df: pd.DataFrame,
    value_col: str,
    weight_col: str = PUMS.PWGTP,
) -> float:
    """Compute weighted sum of value_col using weight_col."""
    return (df[weight_col] * df[value_col]).sum()


def weighted_share(
    df: pd.DataFrame,
    condition: pd.Series,
    weight_col: str = PUMS.PWGTP,
) -> float:
    """Compute weighted share (percentage) of rows meeting condition."""
    w = df[weight_col]
    total = w.sum()
    if total == 0:
        return 0.0
    return (w[condition].sum() / total) * 100


def compute_housing_form_shares(
    df: pd.DataFrame,
    weight_col: str = PUMS.WGTP,
    bld_col: str = PUMS.BLD,
) -> Dict[str, float]:
    """
    Compute housing form shares from BLD codes using centralized categories.

    Returns dict with keys:
        sf_detached, sf_attached, multifamily, mobile, other,
        pct_singlefamily, pct_multifamily
    """
    w = df[weight_col]
    bld = df[bld_col]
    total_w = w.sum()

    if total_w == 0:
        return {cat: 0.0 for cat in Codes.BLD_CATEGORIES.keys()} | {
            "pct_singlefamily": 0.0, "pct_multifamily": 0.0
        }

    shares = {}
    for cat, codes in Codes.BLD_CATEGORIES.items():
        shares[cat] = (w[bld.isin(codes)].sum() / total_w) * 100

    # Derived categories
    shares["pct_singlefamily"] = shares["sf_detached"] + shares["sf_attached"]
    shares["pct_multifamily"] = shares["multifamily"]

    return shares


def add_state_abbreviation(
    df: pd.DataFrame,
    state_col: str = PUMS.STATE,
    new_col: str = "state",
) -> pd.DataFrame:
    """Add state abbreviation column from FIPS code."""
    df = df.copy()
    df[new_col] = df[state_col].map(Geo.FIPS_TO_STATE)
    return df


def compute_hpop_metrics(
    person: pd.DataFrame,
    housing: pd.DataFrame,
    group_col: str = PUMS.STATE,
) -> pd.DataFrame:
    """
    Compute HPOP, owner-occ rate, rent-to-income, price-to-income, and
    housing form shares grouped by group_col.

    Uses identically methodology for any grouping variable (STATE, PUMA, etc.)
    so that aggregations are consistent across levels.
    """
    housing = filter_housing_units(housing)

    def merge_housing(person_df, housing_df, cols):
        """Merge person with housing, keeping only specified housing cols."""
        hcols = cols + [PUMS.SERIALNO, PUMS.STATE]
        return person_df.merge(
            housing_df[hcols],
            on=[PUMS.SERIALNO, PUMS.STATE],
            how="left",
        )

    # ── Owner-occupancy rate (occupied housing units only) ──
    hu = housing[housing[PUMS.TEN].notna()].copy()
    hu["owner_occ"] = hu[PUMS.TEN].isin(Codes.OWNER_OCCUPIED)

    ownocc = hu.groupby(group_col).apply(
        lambda g: pd.Series({
            "owner_occ_rate":
                (g[PUMS.WGTP] * g["owner_occ"]).sum() / g[PUMS.WGTP].sum() * 100,
        })
    ).reset_index()

    # ── HPOP (all adults 18+, including group quarters in denominator) ──
    # Per replication.md spec: numerator = adults in owner-occupied units with
    # RELSHIPP 20-24; denominator = all adults 18+ (no GQ filter).
    df = merge_housing(person, housing, [
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.BLD,
    ])
    df = filter_adults(df)
    df["owner_occ"] = df[PUMS.TEN].isin(Codes.OWNER_OCCUPIED)
    df["is_homeowner"] = df["owner_occ"] & df[PUMS.RELSHIPP].isin(Codes.HOMEOWNER_RELSHIPP)

    hpop = df.groupby(group_col).apply(
        lambda g: pd.Series({
            "hpop":
                (g[PUMS.PWGTP] * g["is_homeowner"]).sum() / g[PUMS.PWGTP].sum() * 100,
        })
    ).reset_index()

    # ── Rent-to-income (adult renters 18+, all adults) ──
    renters = merge_housing(person, housing, [
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.GRNTP, PUMS.HINCP,
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

    rent_income = renters.groupby(group_col).apply(
        lambda g: pd.Series({
            "avg_annual_rent": weighted_mean(g, "annual_rent"),
            "avg_personal_income": weighted_mean(g, PUMS.PINCP),
            "rent_to_income": compute_rent_to_income(g),
            "rent_to_income_household": compute_rent_to_income(
                g[g[PUMS.HINCP].notna() & (g[PUMS.HINCP] > 0)], income_col=PUMS.HINCP
            ),
        })
    ).reset_index()

    # ── Rent-to-income (renter adults 18-64, prime working age) ──
    renters_18_64 = renters[renters[PUMS.AGEP] <= 64].copy()

    rent_income_18_64 = renters_18_64.groupby(group_col).apply(
        lambda g: pd.Series({
            "avg_annual_rent_18_64": weighted_mean(g, "annual_rent"),
            "avg_renter_income_18_64": weighted_mean(g, PUMS.PINCP),
            "rent_to_income_18_64": compute_rent_to_income(g),
            "rent_to_income_household_18_64": compute_rent_to_income(
                g[g[PUMS.HINCP].notna() & (g[PUMS.HINCP] > 0)], income_col=PUMS.HINCP
            ),
        })
    ).reset_index()

    # ── Median income by tenure (per replication.md spec) ──
    tenure_income = df.groupby(group_col).apply(
        lambda g: pd.Series({
            "homeowner_median_income": weighted_median(
                g[g["is_homeowner"]], PUMS.PINCP
            ) if g["is_homeowner"].any() else np.nan,
            "renter_median_income": weighted_median(
                g[g[PUMS.TEN].isin(Codes.RENTER_CODES)], PUMS.PINCP
            ) if g[PUMS.TEN].isin(Codes.RENTER_CODES).any() else np.nan,
        })
    ).reset_index()

    # ── Average income of all adults (18+, housing units, no tenure filter) ──
    all_adults = merge_housing(person, housing, [
        PUMS.TEN, PUMS.TYPEHUGQ,
    ])
    all_adults = filter_housing_units(all_adults)
    all_adults = filter_adults(all_adults)
    all_adults = all_adults[all_adults[PUMS.PINCP].notna()].copy()

    adult_income = all_adults.groupby(group_col).apply(
        lambda g: pd.Series({
            "avg_adult_income": weighted_mean(g, PUMS.PINCP),
        })
    ).reset_index()

    # ── Price-to-income (adult homeowners only) ──
    owners = merge_housing(person, housing, [
        PUMS.TEN, PUMS.TYPEHUGQ, PUMS.VALP,
    ])
    owners = filter_housing_units(owners)
    owners = filter_owners(owners)
    owners = filter_adults(owners)
    owners = owners[
        owners[PUMS.VALP].notna() &
        (owners[PUMS.VALP] > 0) &
        owners[PUMS.PINCP].notna() &
        (owners[PUMS.PINCP] > 0)
    ].copy()

    price_income = owners.groupby(group_col).apply(
        lambda g: pd.Series({
            "avg_property_value": weighted_mean(g, PUMS.VALP),
            "avg_owner_income": weighted_mean(g, PUMS.PINCP),
            "price_to_income": compute_price_to_income(g),
        })
    ).reset_index()

    # ── Housing form shares (adults, from merged BLD) ──
    adults = df[df[PUMS.BLD].notna()].copy()
    bld_to_cat = {}
    for cat, codes in Codes.BLD_CATEGORIES.items():
        for code in codes:
            bld_to_cat[code] = cat
    adults["housing_form"] = adults[PUMS.BLD].map(bld_to_cat)

    form_shares = adults.groupby([group_col, "housing_form"]).apply(
        lambda g: pd.Series({"pop": g[PUMS.PWGTP].sum()})
    ).reset_index()

    total_by_group = adults.groupby(group_col)[PUMS.PWGTP].sum().reset_index(name="total_pop")
    form_shares = form_shares.merge(total_by_group, on=group_col)
    form_shares["pct"] = form_shares["pop"] / form_shares["total_pop"] * 100

    form_wide = form_shares.pivot(index=group_col, columns="housing_form", values="pct").fillna(0).reset_index()
    form_wide["pct_multifamily"] = form_wide.get("multifamily", 0)
    form_wide["pct_singlefamily"] = form_wide.get("sf_detached", 0) + form_wide.get("sf_attached", 0)
    for col in ["sf_detached", "sf_attached", "mobile"]:
        if col not in form_wide.columns:
            form_wide[col] = 0.0

    # ── Combine ──
    result = hpop.merge(ownocc, on=group_col, how="outer")
    result = result.merge(rent_income, on=group_col, how="left")
    result = result.merge(rent_income_18_64, on=group_col, how="left")
    result = result.merge(tenure_income, on=group_col, how="left")
    result = result.merge(adult_income, on=group_col, how="left")
    result = result.merge(price_income, on=group_col, how="left")
    result = result.merge(form_wide, on=group_col, how="left")

    result["gap_pp"] = result["hpop"] - result["owner_occ_rate"]

    return result


def compute_rent_to_income(
    df: pd.DataFrame,
    rent_col: str = "annual_rent",
    income_col: str = PUMS.PINCP,
    weight_col: str = PUMS.PWGTP,
) -> float:
    """Compute weighted average rent-to-income ratio (as decimal, not percent)."""
    avg_rent = weighted_mean(df, rent_col, weight_col)
    avg_income = weighted_mean(df, income_col, weight_col)
    return avg_rent / avg_income if avg_income > 0 else np.nan


def compute_price_to_income(
    df: pd.DataFrame,
    value_col: str = PUMS.VALP,
    income_col: str = PUMS.PINCP,
    weight_col: str = PUMS.PWGTP,
) -> float:
    """Compute weighted average price-to-income ratio."""
    avg_value = weighted_mean(df, value_col, weight_col)
    avg_income = weighted_mean(df, income_col, weight_col)
    return avg_value / avg_income if avg_income > 0 else np.nan


def save_output(
    df: pd.DataFrame,
    filename: str,
    columns: Optional[List[str]] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """
    Save DataFrame to output directory with consistent column ordering.

    Args:
        df: DataFrame to save
        filename: Output filename
        columns: Column ordering (uses OutputColumns.STATE_LEVEL or PUMA_LEVEL if None)
        output_dir: Output directory (defaults to OUT_DIR)

    Returns:
        Path to saved file
    """
    output_dir = output_dir or OUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if columns is not None:
        df = df[columns]

    path = output_dir / filename
    df.to_csv(path, index=False)
    return path


def load_state_data() -> pd.DataFrame:
    """Load state-level HPOP results."""
    return pd.read_csv(OUT_DIR / FileNames.STATE_CSV)


def load_puma_data(state: str = "MS") -> pd.DataFrame:
    """Load PUMA-level metrics for a state."""
    if state == "MS":
        return pd.read_csv(OUT_DIR / "puma" / FileNames.MS_PUMA_CSV)
    elif state == "NY":
        return pd.read_csv(OUT_DIR / "puma" / FileNames.NYC_PUMA_CSV)
    else:
        raise ValueError(f"Unknown state for PUMA data: {state}")


# Export commonly used paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/2024"
OUT_DIR = ROOT / "output"