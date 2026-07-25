#!/usr/bin/env python3
"""Validation script to compare before/after refactoring outputs."""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
BACKUP_DIR = ROOT / "output_backup"


def compare_csvs(file1: Path, file2: Path, key_cols: list, tol: float = 0.01,
                 exclude_cols: list = None) -> tuple[bool, list]:
    """
    Compare two CSV files on key columns.

    Args:
        file1: Path to first CSV (reference)
        file2: Path to second CSV (new)
        key_cols: Columns to use as keys for merging
        tol: Tolerance for numeric comparison
        exclude_cols: Columns to exclude from comparison

    Returns:
        Tuple of (all_match, list_of_differences)
    """
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Align columns
    common_cols = [c for c in df1.columns if c in df2.columns]
    if exclude_cols:
        common_cols = [c for c in common_cols if c not in exclude_cols]

    df1 = df1[common_cols]
    df2 = df2[common_cols]

    # Merge on key columns
    merged = df1.merge(df2, on=key_cols, suffixes=("_ref", "_new"))

    diffs = []
    for col in common_cols:
        if col in key_cols:
            continue
        ref_col = f"{col}_ref"
        new_col = f"{col}_new"
        if ref_col in merged.columns and new_col in merged.columns:
            # For numeric columns, check within tolerance
            if pd.api.types.is_numeric_dtype(merged[ref_col]):
                mask = (merged[ref_col] - merged[new_col]).abs() > tol
                if mask.any():
                    for _, row in merged[mask].iterrows():
                        diffs.append({
                            "key": {k: row[k] for k in key_cols},
                            "column": col,
                            "ref": row[ref_col],
                            "new": row[new_col],
                            "diff": row[ref_col] - row[new_col],
                        })

    return len(diffs) == 0, diffs


def validate_state_level():
    """Validate state-level outputs."""
    print("\n" + "="*60)
    print("VALIDATING STATE-LEVEL OUTPUTS")
    print("="*60)

    ref = OUTPUT_DIR / "hpop_by_state_2024.csv"
    # We don't have a backup - just validate the new output is reasonable
    if not ref.exists():
        print(f"ERROR: {ref} not found")
        return False, []

    df = pd.read_csv(ref)

    checks = []

    # Check all 51 states + DC present (excluding PR=72)
    expected_states = 51
    if len(df) != expected_states:
        checks.append(f"Expected {expected_states} states, got {len(df)}")

    # Check no nulls in key metrics
    key_metrics = ["hpop", "owner_occ_rate", "gap_pp", "rent_to_income", "price_to_income"]
    for col in key_metrics:
        if df[col].isna().any():
            checks.append(f"Null values in {col}")

    # Check reasonable ranges
    if not df["hpop"].between(0, 100).all():
        checks.append("HPOP out of range [0, 100]")
    if not df["owner_occ_rate"].between(0, 100).all():
        checks.append("Owner-occ rate out of range [0, 100]")
    if not df["gap_pp"].between(-50, 50).all():
        checks.append("Gap PP out of range [-50, 50]")
    if not df["rent_to_income"].between(0, 3).all():
        checks.append("Rent-to-income out of range [0, 3]")

    # Housing form shares sum to ~100 (excluding mobile/other)
    form_sum = df["pct_multifamily"] + df["pct_singlefamily"] + df["mobile"]
    if not form_sum.between(95, 105).all():
        checks.append(f"Housing form shares sum to {form_sum.mean():.1f}% (expected ~100%)")

    if checks:
        print("ISSUES FOUND:")
        for c in checks:
            print(f"  - {c}")
        return False, checks

    print(f"All checks passed for {len(df)} states")
    print(f"  HPOP range: {df['hpop'].min():.1f}% - {df['hpop'].max():.1f}%")
    print(f"  Owner-Occ range: {df['owner_occ_rate'].min():.1f}% - {df['owner_occ_rate'].max():.1f}%")
    print(f"  Gap range: {df['gap_pp'].min():.1f} - {df['gap_pp'].max():.1f} pp")
    print(f"  Rent/Income range: {df['rent_to_income'].min():.3f} - {df['rent_to_income'].max():.3f}")

    return True, []


def validate_puma_level():
    """Validate PUMA-level outputs."""
    print("\n" + "="*60)
    print("VALIDATING PUMA-LEVEL OUTPUTS")
    print("="*60)

    all_passed = True
    all_issues = []

    for name, path in [("MS PUMAs", OUTPUT_DIR / "puma" / "ms_puma_metrics.csv"),
                        ("NYC PUMAs", OUTPUT_DIR / "puma" / "nyc_puma_metrics.csv")]:
        if not path.exists():
            print(f"ERROR: {path} not found")
            all_passed = False
            continue

        df = pd.read_csv(path)
        issues = []

        if len(df) == 0:
            issues.append("Empty dataframe")

        # Check key columns
        required = ["hpop", "owner_occ_rate", "gap_pp", "rent_to_income",
                    "multifamily_share"]
        for col in required:
            if col not in df.columns:
                issues.append(f"Missing column: {col}")

        # Check reasonable ranges
        if "hpop" in df.columns and not df["hpop"].between(0, 100).all():
            issues.append("HPOP out of range [0, 100]")

        if issues:
            print(f"\n{name} - ISSUES:")
            for i in issues:
                print(f"  - {i}")
            all_passed = False
            all_issues.extend([f"{name}: {i}" for i in issues])
        else:
            print(f"\n{name} - All checks passed ({len(df)} PUMAs)")
            print(f"  HPOP range: {df['hpop'].min():.1f}% - {df['hpop'].max():.1f}%")
            print(f"  MF share range: {df['multifamily_share'].min():.1f}% - {df['multifamily_share'].max():.1f}%")
            print(f"  SF-detached range: {df['sf_detached_share'].min():.1f}% - {df['sf_detached_share'].max():.1f}%")

    return all_passed, all_issues


def validate_output_files_exist():
    """Check all expected output files exist."""
    print("\n" + "="*60)
    print("CHECKING OUTPUT FILES EXIST")
    print("="*60)

    expected = [
        "hpop_by_state_2024.csv",
        "results.md",
        "gap_vs_rent_to_income.png",
        "owner_occ_vs_multifamily.png",
        "gap_vs_adults_per_unit.png",
        "adults_per_unit_vs_rent_to_income.png",
        "puma/ms_puma_metrics.csv",
        "puma/nyc_puma_metrics.csv",
        "puma/puma_results.md",
        "puma/puma_rent_to_income_vs_gap.png",
        "puma/puma_owner_occ_vs_multifamily.png",
        "puma/puma_gap_vs_adults_per_unit.png",
        "puma/puma_adults_per_unit_vs_rent_to_income.png",
    ]

    missing = []
    for f in expected:
        path = OUTPUT_DIR / f
        if path.exists():
            print(f"  OK: {f}")
        else:
            print(f"  MISSING: {f}")
            missing.append(f)

    return len(missing) == 0, missing


def main():
    """Run all validations."""
    print("HPOP Pipeline Output Validation")
    print("="*60)

    all_passed = True
    all_issues = []

    # Check files exist
    passed, issues = validate_output_files_exist()
    if not passed:
        all_passed = False
        all_issues.extend(issues)

    # Validate state-level
    passed, issues = validate_state_level()
    if not passed:
        all_passed = False
        all_issues.extend(issues)

    # Validate PUMA-level
    passed, issues = validate_puma_level()
    if not passed:
        all_passed = False
        all_issues.extend(issues)

    print("\n" + "="*60)
    if all_passed:
        print("ALL VALIDATIONS PASSED")
        return 0
    else:
        print("VALIDATION FAILED")
        print("\nIssues:")
        for issue in all_issues:
            print(f"  - {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())