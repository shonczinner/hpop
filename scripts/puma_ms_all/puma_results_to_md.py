#!/usr/bin/env python3
"""Generate markdown report for PUMA-level HPOP analysis."""
import pandas as pd
import numpy as np
from pathlib import Path

from scripts.constants import (
    FileNames, ROOT, OUT_DIR, PUMA_OUT_DIR
)
from scripts.utils import load_state_data, load_puma_data


def main():
    ms_puma = load_puma_data("MS")
    nyc_puma = load_puma_data("NY")

    state_df = load_state_data()
    ms_state = state_df[state_df["state"] == "MS"].iloc[0]
    ny_state = state_df[state_df["state"] == "NY"].iloc[0]

    lines = []
    lines.append("# PUMA-Level HPOP Analysis — Mississippi vs NYC\n")

    # ── Summary Stats ──
    lines.append("## Summary Statistics\n")
    lines.append("| Metric | Mississippi (PUMAs) | NYC (PUMAs) | Mississippi (state) | New York (state) |")
    lines.append("|--------|-------------------|-------------|--------------------|-----------------|")
    lines.append(f"| Count | {len(ms_puma)} PUMAs | {len(nyc_puma)} PUMAs | 1 state | 1 state |")
    lines.append(f"| Mean HPOP | {ms_puma['hpop'].mean():.1f}% | {nyc_puma['hpop'].mean():.1f}% | {ms_state['hpop']:.1f}% | {ny_state['hpop']:.1f}% |")
    lines.append(f"| Mean Owner-Occ | {ms_puma['owner_occ_rate'].mean():.1f}% | {nyc_puma['owner_occ_rate'].mean():.1f}% | {ms_state['owner_occ_rate']:.1f}% | {ny_state['owner_occ_rate']:.1f}% |")
    lines.append(f"| Mean Gap (Owner-Occ − HPOP) | {ms_puma['gap_pp'].mean():.1f} pp | {nyc_puma['gap_pp'].mean():.1f} pp | {ms_state['gap_pp']:.1f} pp | {ny_state['gap_pp']:.1f} pp |")
    lines.append(f"| Mean Multifamily | {ms_puma['multifamily_share'].mean():.1f}% | {nyc_puma['multifamily_share'].mean():.1f}% | {ms_state['pct_multifamily']:.1f}% | {ny_state['pct_multifamily']:.1f}% |")
    lines.append(f"| Mean Rent-to-Income | {ms_puma['rent_to_income'].mean():.1f}% | {nyc_puma['rent_to_income'].mean():.1f}% | — | — |")
    lines.append(f"| Mean Rent-to-Income 18-64 | {ms_puma['rent_to_income_18_64'].mean():.1f}% | {nyc_puma['rent_to_income_18_64'].mean():.1f}% | — | — |")
    income_ms = ms_state['avg_adult_income']
    income_ny = ny_state['avg_adult_income']
    lines.append(f"| Mean Adult Income | ${ms_puma['mean_adult_income'].mean():,.0f} | ${nyc_puma['mean_adult_income'].mean():,.0f} | ${income_ms:,.0f} | ${income_ny:,.0f} |")
    lines.append("")

    # ── Correlations ──
    mf_corr_ms = ms_puma["multifamily_share"].corr(ms_puma["gap_pp"].mul(-1))
    mf_corr_nyc = nyc_puma["multifamily_share"].corr(nyc_puma["gap_pp"].mul(-1))
    rent_corr_ms = ms_puma["rent_to_income"].corr(ms_puma["gap_pp"].mul(-1))
    rent_corr_nyc = nyc_puma["rent_to_income"].corr(nyc_puma["gap_pp"].mul(-1))
    rent18_corr_ms = ms_puma["rent_to_income_18_64"].corr(ms_puma["gap_pp"].mul(-1))
    rent18_corr_nyc = nyc_puma["rent_to_income_18_64"].corr(nyc_puma["gap_pp"].mul(-1))
    income_corr_ms = ms_puma["mean_adult_income"].corr(ms_puma["gap_pp"].mul(-1))
    income_corr_nyc = nyc_puma["mean_adult_income"].corr(nyc_puma["gap_pp"].mul(-1))

    lines.append("## Correlations vs Gap (neg_gap)\n")
    lines.append("| Variable | MS PUMAs (r) | NYC PUMAs (r) |")
    lines.append("|----------|--------------|---------------|")
    lines.append(f"| Multifamily Share | {mf_corr_ms:.3f} | {mf_corr_nyc:.3f} |")
    lines.append(f"| Rent-to-Income 18+ | {rent_corr_ms:.3f} | {rent_corr_nyc:.3f} |")
    lines.append(f"| Rent-to-Income 18-64 | {rent18_corr_ms:.3f} | {rent18_corr_nyc:.3f} |")
    lines.append(f"| Avg Adult Income | {income_corr_ms:.3f} | {income_corr_nyc:.3f} |")
    lines.append("")

    # ── All MS PUMAs ──
    lines.append("## Mississippi PUMA Details\n")
    lines.append("| PUMA | Name | HPOP | Owner-Occ | Gap | Multifamily | Rent/Inc | Rent/Inc 18-64 |")
    lines.append("|------|------|------|-----------|-----|-------------|----------|----------------|")
    for _, row in ms_puma.sort_values("gap_pp").iterrows():
        lines.append(
            f"| {row['puma']} | {row['name']} | {row['hpop']:.1f}% | {row['owner_occ_rate']:.1f}% | "
            f"{row['gap_pp']:+.1f} | {row['multifamily_share']:.1f}% | "
            f"{row['rent_to_income']:.1f}% | {row['rent_to_income_18_64']:.1f}% |"
        )
    lines.append("")

    # ── All NYC PUMAs ──
    lines.append("## NYC PUMA Details\n")
    lines.append("| PUMA | Name | HPOP | Owner-Occ | Gap | Multifamily | Rent/Inc | Rent/Inc 18-64 |")
    lines.append("|------|------|------|-----------|-----|-------------|----------|----------------|")
    for _, row in nyc_puma.sort_values("gap_pp").iterrows():
        lines.append(
            f"| {row['puma']} | {row['name']} | {row['hpop']:.1f}% | {row['owner_occ_rate']:.1f}% | "
            f"{row['gap_pp']:+.1f} | {row['multifamily_share']:.1f}% | "
            f"{row['rent_to_income']:.1f}% | {row['rent_to_income_18_64']:.1f}% |"
        )
    lines.append("")

    # ── Key Findings ──
    lines.append("## Key Findings\n")
    lines.append("1. **Multifamily share is the universal predictor** of the HPOP/Owner-Occ gap — higher multifamily → smaller gap (less Owner-Occ > HPOP). r = "
                 f"{mf_corr_ms:.3f} (MS) and {mf_corr_nyc:.3f} (NYC).\n")
    lines.append("2. **Gap sign flips**: state-level MS shows Owner-Occ > HPOP, but dense urban NYC PUMAs "
                 "show Owner-Occ < HPOP due to high multifamily concentration.\n")
    lines.append("3. **Rent-to-income at PUMA level** (all 18+): r = "
                 f"{rent_corr_ms:.2f} (MS) and {rent_corr_nyc:.2f} (NYC). "
                 f"Ages 18-64: r = {rent18_corr_ms:.2f} (MS) and {rent18_corr_nyc:.2f} (NYC). "
                 "Weaker than at state level, suggesting rent burden is more of a regional than neighborhood phenomenon. "
                 f"See scatter plots below.\n")
    ny_mf = ny_state['pct_multifamily']
    nyc_mf_min = nyc_puma['multifamily_share'].min()
    nyc_mf_max = nyc_puma['multifamily_share'].max()
    lines.append(f"4. **NY state vs NYC PUMAs**: New York state's multifamily share ({ny_mf:.1f}%) "
                 f"sits below most NYC PUMAs ({nyc_mf_min:.1f}%–{nyc_mf_max:.1f}%), "
                 "reflecting upstate's lower density.\n")
    lines.append("### Rent-to-Income Plots\n")
    lines.append(f"![Rent-to-Income 18+ vs Gap]({FileNames.PLOT_PUMA_RENT_VS_GAP})\n")
    lines.append(f"![Rent-to-Income 18-64 vs Gap]({FileNames.PLOT_PUMA_RENT_VS_GAP_18_64})\n")
    lines.append("### Income vs Gap\n")
    lines.append(f"![Adult Income vs Gap]({FileNames.PLOT_PUMA_GAP_VS_INCOME})\n")

    md = "\n".join(lines)
    (PUMA_OUT_DIR / FileNames.PUMA_MD).write_text(md)
    print(md)


if __name__ == "__main__":
    main()