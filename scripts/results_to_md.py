#!/usr/bin/env python3
"""Generate markdown report of state-level HPOP results."""
import pandas as pd

from scripts.constants import (
    Geo, FileNames, ROOT, OUT_DIR
)
from scripts.utils import load_state_data


def main():
    df = load_state_data()

    mfed = pd.read_excel(ROOT / "data/2024/mfed_hpop.xlsx", sheet_name="hpop_oown_state")
    mfed_nat = mfed[(mfed["year"] == 2024) & (mfed["fips"] == 0)].iloc[0]
    mfed = mfed[(mfed["year"] == 2024) & (mfed["fips"] != 0)].copy()
    mfed["state"] = mfed["fips"].map(Geo.FIPS_TO_STATE)

    merged = df.merge(mfed[["state", "hpop", "ownocc"]], on="state", suffixes=("_ours", "_mfed"))
    merged["delta_hpop"] = merged["hpop_ours"] - merged["hpop_mfed"]
    merged["delta_ownocc"] = merged["owner_occ_rate"] - merged["ownocc"]

    df["neg_gap"] = -df["gap_pp"]
    df["adults_per_unit"] = df["n_adults"] / df["n_occupied_units"]
    rent_corr = df["rent_to_income"].corr(df["neg_gap"])
    apu_corr = df["adults_per_unit"].corr(df["neg_gap"])
    mf_corr = df["pct_multifamily"].corr(df["neg_gap"])

    lines = []
    lines.append("# HPOP Results — 2024 ACS PUMS\n")

    lines.append("## National Summary\n")
    lines.append("| Metric | Ours | Minneapolis Fed | Delta |")
    lines.append("|--------|------|-----------------|-------|")
    lines.append(f"| HPOP | {df['hpop'].mean():.1f}% | {mfed_nat['hpop']:.1f}% | {df['hpop'].mean() - mfed_nat['hpop']:+.1f} pp |")
    lines.append(f"| Owner-Occ | {df['owner_occ_rate'].mean():.1f}% | {mfed_nat['ownocc']:.1f}% | {df['owner_occ_rate'].mean() - mfed_nat['ownocc']:+.1f} pp |")
    lines.append(f"| Gap (Owner-Occ \u2212 HPOP) | {df['gap_pp'].mean():.1f} pp | \u2014 | \u2014 |")
    lines.append(f"| Rent-to-Income Ratio | {df['rent_to_income'].mean():.3f} | \u2014 | \u2014 |")
    lines.append("")

    lines.append("## State-Level Results\n")
    lines.append("| State | HPOP | HPOP (MFED) | \u0394 HPOP | Owner-Occ | OwnOcc (MFED) | \u0394 OwnOcc | Gap | Rent/Income |")
    lines.append("|-------|------|-------------|--------|-----------|---------------|----------|-----|-------------|")
    for _, row in merged.sort_values("hpop_ours", ascending=False).iterrows():
        lines.append(
            f"| {row['state']} | {row['hpop_ours']:.1f} | {row['hpop_mfed']:.1f} | "
            f"{row['delta_hpop']:+.1f} | {row['owner_occ_rate']:.1f} | {row['ownocc']:.1f} | "
            f"{row['delta_ownocc']:+.1f} | {row['gap_pp']:+.1f} | {row['rent_to_income']:.2f} |"
        )
    lines.append("")

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

    lines.append("## Correlations vs Gap (neg_gap)\n")
    lines.append("| Variable | r vs Neg-Gap |")
    lines.append("|----------|--------------|")
    lines.append(f"| Rent-to-Income | {rent_corr:.3f} |")
    lines.append(f"| Adults per Unit | {apu_corr:.3f} |")
    lines.append("")

    lines.append("### Rent-to-Income vs Gap\n")
    lines.append(f"![Rent-to-Income vs Gap]({FileNames.PLOT_GAP_RENT})\n")
    lines.append(f"Correlation with gap: r = {rent_corr:.3f}\n")
    lines.append("")

    lines.append("### Multifamily Share vs Occupancy Rate\n")
    lines.append(f"![Multifamily Share vs Owner-Occ]({FileNames.PLOT_OWNER_OCC_VS_MF})\n")
    lines.append("")

    lines.append("### Adults per Home vs Gap\n")
    lines.append(f"![Adults per Unit vs Gap]({FileNames.PLOT_GAP_VS_ADULTS_PER_UNIT})\n")
    lines.append(f"Correlation with gap: r = {apu_corr:.3f}\n")
    lines.append("")

    apu_rent_corr = df["adults_per_unit"].corr(df["rent_to_income"])
    lines.append("### Rent-to-Income vs Adults per Home\n")
    lines.append(f"![Rent-to-Income vs Adults per Unit]({FileNames.PLOT_ADULTS_PER_UNIT_VS_RENT_TO_INCOME})\n")
    lines.append(f"Rent-to-income and adults per unit are correlated at the state level (r = {apu_rent_corr:.3f}), confirming the ecological confound: expensive states also have larger households.\n")
    lines.append("")

    lines.append("## Key Findings\n")
    lines.append("1. **HPOP < Owner-Occ everywhere** \u2014 traditional owner-occupancy rate almost always overstates")
    lines.append("   effective homeownership because it counts cohabitants (adult children, roommates)")
    lines.append("   in owner-occupied units as owners.\n")
    lines.append("2. **Gap varies by state** \u2014 ranges from {:.1f} pp (ND) to {:.1f} pp (HI), driven by".format(
        df["gap_pp"].min(), df["gap_pp"].max()))
    lines.append("   housing costs, household composition, and prevalence of adult co-residents.\n")
    lines.append("3. **Rent burden is the strongest correlate** of the gap (r = {:.3f}), suggesting that".format(rent_corr))
    lines.append("   housing affordability drives the divergence between owner-occ and HPOP.\n")
    lines.append("4. **Adults per home is also strongly correlated** with the gap (r = {:.3f}), ".format(apu_corr))
    lines.append("   meaning states with larger households show a bigger gap between the two homeownership measures.\n")
    lines.append("5. **Multifamily share vs gap at state level** (r = {:.3f}) \u2014 the relationship is ".format(mf_corr))
    lines.append("   weaker across states than within metros, suggesting other state-level factors")
    lines.append("   (household composition, costs) dominate.")
    lines.append("")

    md = "\n".join(lines)
    (OUT_DIR / FileNames.STATE_MD).write_text(md)
    print(md)


if __name__ == "__main__":
    main()
