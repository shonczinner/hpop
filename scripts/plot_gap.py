#!/usr/bin/env python3
"""Plot HPOP gap vs cost metrics (rent-to-income and price-to-income)."""
import numpy as np

from scripts.constants import (
    PlotStyle, FileNames, OUT_DIR
)
from scripts.utils import load_state_data
from scripts.plot_utils import (
    setup_figure, style_scatter, add_fit_line, add_correlation_text,
    annotate_points, set_axis_labels, save_figure
)


def main():
    df = load_state_data()
    df["neg_gap"] = -df["gap_pp"]
    adults_per_unit = df["n_adults"].values / df["n_occupied_units"].values

    # ── Plot 1: Rent-to-Income vs Gap ──
    fig, ax = setup_figure()
    style_scatter(ax, df["rent_to_income"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax, df, "rent_to_income", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])
    r = add_fit_line(ax, df["rent_to_income"].values, df["neg_gap"].values, "fit_line", x_pad=0.05)
    add_correlation_text(ax, {"State": r})
    set_axis_labels(
        ax,
        "Rent-to-Income Ratio (avg annual rent / avg renter income)",
        "Owner-Occ \u2212 HPOP Rate (percentage points)",
        "Housing Costs vs. Homeownership Measure Gap by State (2024)",
        x_format="%.2f",
    )
    save_figure(fig, FileNames.PLOT_GAP_RENT, out_dir=OUT_DIR)

    # ── Plot 2: Multifamily Share vs Owner-Occupancy Rate ──
    fig2, ax2 = setup_figure()
    style_scatter(ax2, df["pct_multifamily"].values, df["owner_occ_rate"].values, "scatter_main", "State")
    annotate_points(ax2, df, "pct_multifamily", "owner_occ_rate", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])
    r2 = add_fit_line(ax2, df["pct_multifamily"].values, df["owner_occ_rate"].values, "fit_line")
    add_correlation_text(ax2, {"State": r2})
    set_axis_labels(
        ax2,
        "Multifamily Share (% of occupied units)",
        "Owner-Occupancy Rate (% of occupied units)",
        "Homeownership vs. Multifamily Share by State (2024)",
        x_format=PlotStyle.X_FORMAT_PCT,
    )
    save_figure(fig2, FileNames.PLOT_OWNER_OCC_VS_MF, out_dir=OUT_DIR)

    # ── Plot 3: Adults per Home vs Gap ──
    fig3, ax3 = setup_figure()
    style_scatter(ax3, adults_per_unit, df["neg_gap"].values, "scatter_main", "State")
    for _, row in df.iterrows():
        ax3.annotate(
            row["state"], (row["n_adults"] / row["n_occupied_units"], row["neg_gap"]),
            fontsize=PlotStyle.FONT_SIZES["annotation"], ha="center", va="bottom",
            xytext=(0, 5), textcoords="offset points",
        )
    r3 = add_fit_line(ax3, adults_per_unit, df["neg_gap"].values, "fit_line")
    add_correlation_text(ax3, {"State": r3})
    x_pad = (adults_per_unit.max() - adults_per_unit.min()) * 0.05
    y_pad = (df["neg_gap"].max() - df["neg_gap"].min()) * 0.05
    ax3.set_xlim(adults_per_unit.min() - x_pad, adults_per_unit.max() + x_pad)
    ax3.set_ylim(df["neg_gap"].min() - y_pad, df["neg_gap"].max() + y_pad)
    set_axis_labels(
        ax3,
        "Adults per Occupied Housing Unit",
        "Owner-Occ \u2212 HPOP Rate (percentage points)",
        "Household Size vs. Homeownership Measure Gap by State (2024)",
    )
    save_figure(fig3, FileNames.PLOT_GAP_VS_ADULTS_PER_UNIT, out_dir=OUT_DIR)

    # ── Plot 4: Rent-to-Income vs Adults per Home ──
    fig4, ax4 = setup_figure()
    style_scatter(ax4, df["rent_to_income"].values, adults_per_unit, "scatter_main", "State")
    for _, row in df.iterrows():
        ax4.annotate(
            row["state"], (row["rent_to_income"], row["n_adults"] / row["n_occupied_units"]),
            fontsize=PlotStyle.FONT_SIZES["annotation"], ha="center", va="bottom",
            xytext=(0, 5), textcoords="offset points",
        )
    r4 = add_fit_line(ax4, df["rent_to_income"].values, adults_per_unit, "fit_line")
    add_correlation_text(ax4, {"State": r4})
    x_pad = (df["rent_to_income"].max() - df["rent_to_income"].min()) * 0.05
    y_pad = (adults_per_unit.max() - adults_per_unit.min()) * 0.05
    ax4.set_xlim(df["rent_to_income"].min() - x_pad, df["rent_to_income"].max() + x_pad)
    ax4.set_ylim(adults_per_unit.min() - y_pad, adults_per_unit.max() + y_pad)
    set_axis_labels(
        ax4,
        "Rent-to-Income Ratio (avg annual rent / avg renter income)",
        "Adults per Occupied Housing Unit",
        "Rent-to-Income vs. Household Size by State (2024)",
        x_format="%.2f",
    )
    save_figure(fig4, FileNames.PLOT_ADULTS_PER_UNIT_VS_RENT_TO_INCOME, out_dir=OUT_DIR)


if __name__ == "__main__":
    main()
