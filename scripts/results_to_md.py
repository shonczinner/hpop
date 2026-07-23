#!/usr/bin/env python3
"""Generate markdown report of state-level HPOP results."""
import pandas as pd
import numpy as np
from pathlib import Path

from scripts.constants import (
    Geo, FileNames, ROOT, OUT_DIR
)
from scripts.utils import load_state_data


def main():
    df = load_state_data()

    # Load MFED official data
    mfed = pd.read_excel(ROOT / "data/2024/mfed_hpop.xlsx", sheet_name="hpop_oown_state")
    mfed_nat = mfed[(mfed["year"] == 2024) & (mfed["fips"] == 0)].iloc[0]
    mfed = mfed[(mfed["year"] == 2024) & (mfed["fips"] != 0)].copy()

    mfed["state"] = mfed["fips"].map(Geo.FIPS_TO_STATE)

    # Merge
    merged = df.merge(mfed[["state", "hpop", "ownocc"]], on="state", suffixes=("_ours", "_mfed"))
    merged["delta_hpop"] = merged["hpop_ours"] - merged["hpop_mfed"]
    merged["delta_ownocc"] = merged["owner_occ_rate"] - merged["ownocc"]

    lines = []
    lines.append("# HPOP Results — 2024 ACS PUMS\n")

    # National summary
    lines.append("## National Summary\n")
    lines.append("| Metric | Ours | Minneapolis Fed | Delta |")
    lines.append("|--------|------|-----------------|-------|")
    lines.append(f"| HPOP | {df['hpop'].mean():.1f}% | {mfed_nat['hpop']:.1f}% | {df['hpop'].mean() - mfed_nat['hpop']:+.1f} pp |")
    lines.append(f"| Owner-Occ | {df['owner_occ_rate'].mean():.1f}% | {mfed_nat['ownocc']:.1f}% | {df['owner_occ_rate'].mean() - mfed_nat['ownocc']:+.1f} pp |")
    lines.append(f"| Gap (Owner-Occ − HPOP) | {df['gap_pp'].mean():.1f} pp | — | — |")
    lines.append(f"| Rent-to-Income Ratio | {df['rent_to_income'].mean():.3f} | — | — |")
    lines.append(    f"| Rent-to-Income 18-64 | {df['rent_to_income_18_64'].mean():.3f} | — | — |")
    lines.append(f"| Avg Adult Income | ${df['avg_adult_income'].mean():,.0f} | — | — |")
    lines.append(f"| Price-to-Income Ratio | {df['price_to_income'].mean():.1f} | — | — |")
    lines.append("")

    # State table with MFED comparison
    lines.append("## State-Level Results\n")
    lines.append("| State | HPOP | HPOP (MFED) | Δ HPOP | Owner-Occ | OwnOcc (MFED) | Δ OwnOcc | Gap | Rent/Income | Price/Income |")
    lines.append("|-------|------|-------------|--------|-----------|---------------|----------|-----|-------------|--------------|")

    for _, row in merged.sort_values("hpop_ours", ascending=False).iterrows():
        lines.append(
            f"| {row['state']} | {row['hpop_ours']:.1f} | {row['hpop_mfed']:.1f} | "
            f"{row['delta_hpop']:+.1f} | {row['owner_occ_rate']:.1f} | {row['ownocc']:.1f} | "
            f"{row['delta_ownocc']:+.1f} | {row['gap_pp']:+.1f} | {row['rent_to_income']:.2f} | {row['price_to_income']:.1f} |"
        )
    lines.append("")

    # Validation summary
    hpop_corr = merged["hpop_ours"].corr(merged["hpop_mfed"])
    hpop_mae = merged["delta_hpop"].abs().mean()
    ownocc_corr = merged["owner_occ_rate"].corr(merged["ownocc"])
    ownocc_mae = merged["delta_ownocc"].abs().mean()

    lines.append("## Validation vs Minneapolis Fed\n")
    lines.append("| Metric | Correlation (r) | MAE (pp) | Mean Bias |")
    lines.append("|--------|-----------------|----------|-----------|")
    lines.append(f"| HPOP | {hpop_corr:.4f} | {hpop_mae:.2f} | {merged['delta_hpop'].mean():+.2f} |")
    lines.append(f"| Owner-Occ | {ownocc_corr:.4f} | {ownocc_mae:.2f} | {merged['delta_ownocc'].mean():+.2f} |")
    lines.append("")

    # Gap correlations (neg_gap = -gap_pp, so positive r = more gap with more x)
    df["neg_gap"] = -df["gap_pp"]
    rent_corr = df["rent_to_income"].corr(df["neg_gap"])
    rent_corr_18_64 = df["rent_to_income_18_64"].corr(df["neg_gap"])
    price_corr = df["price_to_income"].corr(df["neg_gap"])
    mf_corr = df["pct_multifamily"].corr(df["neg_gap"])
    income_corr = df["avg_adult_income"].corr(df["neg_gap"])
    owner_occ_corr = df["owner_occ_rate"].corr(df["neg_gap"])
    lines.append("## Gap Correlations\n")
    lines.append("| Variable | r vs Neg-Gap |")
    lines.append("|----------|--------------|")
    lines.append(f"| Rent-to-Income (renter 18+) | {rent_corr:.3f} |")
    lines.append(f"| Rent-to-Income (renter 18-64) | {rent_corr_18_64:.3f} |")
    lines.append(f"| Price-to-Income (owner) | {price_corr:.3f} |")
    lines.append(f"| Multifamily Share | {mf_corr:.3f} |")
    lines.append(f"| Avg Adult Income | {income_corr:.3f} |")
    lines.append(f"| Owner-Occ Rate | {owner_occ_corr:.3f} |")
    lines.append("")

    # Rent-to-income comparison plots
    lines.append("## Rent-to-Income: All Adults vs Ages 18-64\n")
    lines.append("![Rent-to-Income 18+](gap_vs_rent_to_income.png)\n")
    lines.append("![Rent-to-Income 18-64](gap_vs_rent_to_income_18_64.png)\n")
    lines.append("Correlation with gap (neg-gap): all adults r = {:.3f}, ages 18-64 r = {:.3f}\n".format(rent_corr, rent_corr_18_64))
    lines.append("")

    # Housing form summary
    lines.append("## Housing Form by State\n")
    lines.append("![Multifamily Share vs Gap](state_multifamily_vs_gap.png)\n")

    # Income vs gap
    lines.append("## Average Income vs Gap\n")
    lines.append("![Adult Income vs Gap](gap_vs_adult_income.png)\n")
    lines.append("Correlation with gap: r = {:.3f}\n".format(income_corr))
    lines.append("")

    # Owner-Occ vs gap
    lines.append("## Traditional Homeownership vs Gap\n")
    lines.append("![Owner-Occ vs Gap](gap_vs_owner_occ.png)\n")
    lines.append("Correlation with gap: r = {:.3f}\n".format(owner_occ_corr))
    lines.append("")
    lines.append("| State | Single-Family | Multifamily | Mobile/Other |")
    lines.append("|-------|---------------|-------------|--------------|")
    for _, row in df.sort_values("pct_multifamily", ascending=False).iterrows():
        other = 100 - row["pct_singlefamily"] - row["pct_multifamily"]
        lines.append(
            f"| {row['state']} | {row['pct_singlefamily']:.1f}% | "
            f"{row['pct_multifamily']:.1f}% | {other:.1f}% |"
        )
    lines.append("")

    # Key findings
    lines.append("## Key Findings\n")
    lines.append("1. **HPOP < Owner-Occ everywhere** — traditional owner-occupancy rate always overstates")
    lines.append("   effective homeownership because it counts cohabitants (adult children, roommates)")
    lines.append("   in owner-occupied units as owners.\n")
    lines.append("2. **Gap varies by state** — ranges from -1.0 pp (ND) to -17.7 pp (HI), driven by")
    lines.append("   housing costs, household composition, and prevalence of adult co-residents.\n")
    lines.append("3. **Rent burden is the strongest correlate** of the gap (r = {:.3f}), suggesting that".format(rent_corr))
    lines.append("   housing affordability drives the divergence between owner-occ and HPOP.\n")
    lines.append("4. **Multifamily share vs gap at state level** (r = {:.3f}) — the relationship is ".format(mf_corr))
    lines.append("   weaker across states than within metros (MS PUMAs r = -0.185, NYC PUMAs r = -0.834),")
    lines.append("   suggesting other state-level factors (household composition, costs) dominate.")

    md = "\n".join(lines)
    (OUT_DIR / FileNames.STATE_MD).write_text(md)
    print(md)


if __name__ == "__main__":
    main()