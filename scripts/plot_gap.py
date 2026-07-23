#!/usr/bin/env python3
"""Plot HPOP gap vs cost metrics (rent-to-income and price-to-income)."""
import pandas as pd
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

    # ── Plot 1: Gap vs Rent-to-Income ──
    fig, ax = setup_figure()

    style_scatter(ax, df["rent_to_income"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax, df, "rent_to_income", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r = add_fit_line(ax, df["rent_to_income"].values, df["neg_gap"].values, "fit_line", x_pad=0.05)
    add_correlation_text(ax, {"State": r})

    set_axis_labels(
        ax,
        "Rent-to-Income Ratio (avg annual rent / avg renter income)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Housing Costs vs. Homeownership Measure Gap by State (2024)",
        x_format="%.2f",
    )

    save_figure(fig, FileNames.PLOT_GAP_RENT, out_dir=OUT_DIR)

    # ── Plot 2: Gap vs Price-to-Income ──
    fig2, ax2 = setup_figure()

    style_scatter(ax2, df["price_to_income"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax2, df, "price_to_income", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r2 = add_fit_line(ax2, df["price_to_income"].values, df["neg_gap"].values, "fit_line", x_pad=0.5)
    add_correlation_text(ax2, {"State": r2})

    set_axis_labels(
        ax2,
        "Price-to-Income Ratio (avg property value / avg owner income)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Home Values vs. Homeownership Measure Gap by State (2024)",
        x_format="%.1f",
    )

    save_figure(fig2, FileNames.PLOT_GAP_PRICE, out_dir=OUT_DIR)

    # ── Plot 3: Gap vs Multifamily Share (state level) ──
    fig3, ax3 = setup_figure()

    style_scatter(ax3, df["pct_multifamily"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax3, df, "pct_multifamily", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r3 = add_fit_line(ax3, df["pct_multifamily"].values, df["neg_gap"].values, "fit_line")
    add_correlation_text(ax3, {"State": r3})

    set_axis_labels(
        ax3,
        "Multifamily Share (% of occupied units)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Housing Form vs. Homeownership Measure Gap by State (2024)",
        x_format=PlotStyle.X_FORMAT_PCT,
    )

    save_figure(fig3, FileNames.PLOT_STATE_MF_VS_GAP, out_dir=OUT_DIR)

    # ── Plot 4: Gap vs Rent-to-Income 18-64 (prime working age) ──
    fig4, ax4 = setup_figure()

    style_scatter(ax4, df["rent_to_income_18_64"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax4, df, "rent_to_income_18_64", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r4 = add_fit_line(ax4, df["rent_to_income_18_64"].values, df["neg_gap"].values, "fit_line", x_pad=0.05)
    add_correlation_text(ax4, {"State": r4})

    set_axis_labels(
        ax4,
        "Rent-to-Income Ratio 18-64 (avg annual rent / avg renter income)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Housing Costs vs. Homeownership Measure Gap by State (2024)\nRenters Ages 18-64",
        x_format="%.2f",
    )

    save_figure(fig4, FileNames.PLOT_GAP_RENT_18_64, out_dir=OUT_DIR)

    # ── Plot 5: Gap vs All-Adult Income (unfiltered by tenure) ──
    fig5, ax5 = setup_figure()

    style_scatter(ax5, df["avg_adult_income"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax5, df, "avg_adult_income", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r5 = add_fit_line(ax5, df["avg_adult_income"].values, df["neg_gap"].values, "fit_line", x_pad=5000)
    add_correlation_text(ax5, {"State": r5})

    set_axis_labels(
        ax5,
        "Average Annual Personal Income (All Adults 18+)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Average Income vs. Homeownership Measure Gap by State (2024)",
        x_format="$%.0f",
    )

    save_figure(fig5, FileNames.PLOT_GAP_VS_INCOME, out_dir=OUT_DIR)

    # ── Plot 6: Gap vs Owner-Occ (traditional homeownership rate) ──
    fig6, ax6 = setup_figure()

    style_scatter(ax6, df["owner_occ_rate"].values, df["neg_gap"].values, "scatter_main", "State")
    annotate_points(ax6, df, "owner_occ_rate", "neg_gap", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r6 = add_fit_line(ax6, df["owner_occ_rate"].values, df["neg_gap"].values, "fit_line", x_pad=2)
    add_correlation_text(ax6, {"State": r6})

    set_axis_labels(
        ax6,
        "Owner-Occupancy Rate (% of occupied units)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Traditional Homeownership vs. Measure Gap by State (2024)",
        x_format=PlotStyle.X_FORMAT_PCT,
    )

    save_figure(fig6, FileNames.PLOT_GAP_VS_OWNER_OCC, out_dir=OUT_DIR)

    # ── Plot 7: Owner-Occ vs Multifamily Share (state level) ──
    fig7, ax7 = setup_figure()

    style_scatter(ax7, df["pct_multifamily"].values, df["owner_occ_rate"].values, "scatter_main", "State")
    annotate_points(ax7, df, "pct_multifamily", "owner_occ_rate", "state",
                    fontsize=PlotStyle.FONT_SIZES["annotation"])

    r7 = add_fit_line(ax7, df["pct_multifamily"].values, df["owner_occ_rate"].values, "fit_line")
    add_correlation_text(ax7, {"State": r7})

    set_axis_labels(
        ax7,
        "Multifamily Share (% of occupied units)",
        "Owner-Occupancy Rate (% of occupied units)",
        "Homeownership vs. Multifamily Share by State (2024)",
        x_format=PlotStyle.X_FORMAT_PCT,
    )

    save_figure(fig7, FileNames.PLOT_OWNER_OCC_VS_MF, out_dir=OUT_DIR)


if __name__ == "__main__":
    main()