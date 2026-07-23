#!/usr/bin/env python3
"""Plot housing form vs gap and rent-to-income: MS state, MS PUMAs, NYC PUMAs, NY state."""
import pandas as pd
import numpy as np

from scripts.constants import (
    PlotStyle, FileNames, OUT_DIR, PUMA_OUT_DIR
)
from scripts.utils import load_state_data, load_puma_data
from scripts.plot_utils import (
    setup_figure, style_scatter, add_fit_line, add_correlation_text,
    set_axis_labels, add_legend, save_figure,
)


def main():
    state_df = load_state_data()
    ms_state = state_df[state_df["state"] == "MS"].iloc[0]
    ms_state_neg_gap = -ms_state["gap_pp"]
    ny_state = state_df[state_df["state"] == "NY"].iloc[0]
    ny_state_neg_gap = -ny_state["gap_pp"]

    ms_puma = load_puma_data("MS")
    ms_puma["neg_gap"] = -ms_puma["gap_pp"]

    nyc_puma = load_puma_data("NY")
    nyc_puma["neg_gap"] = -nyc_puma["gap_pp"]

    # ── Plot 1: Multifamily Share vs Gap ──
    fig, ax = setup_figure()

    style_scatter(
        ax, np.array([ms_state["pct_multifamily"]]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax, np.array([ny_state["pct_multifamily"]]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax, ms_puma["multifamily_share"].values, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax, nyc_puma["multifamily_share"].values, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms = add_fit_line(ax, ms_puma["multifamily_share"].values, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc = add_fit_line(ax, nyc_puma["multifamily_share"].values, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(
        ax, {"MS PUMAs": r_ms, "NYC PUMAs": r_nyc},
    )

    set_axis_labels(
        ax,
        "Multifamily Share (% of occupied units in BLD 3-9)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Housing Type vs. Homeownership Measure Gap\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_PCT,
    )
    add_legend(ax, loc="upper left")
    save_figure(fig, FileNames.PLOT_MF_VS_GAP, out_dir=PUMA_OUT_DIR)

    # ── Plot 2: Rent-to-Income vs Gap (PUMA level) ──
    fig2, ax2 = setup_figure()

    # State-level rent_to_income is decimal (0-1), convert to % to match PUMA scale
    style_scatter(
        ax2, np.array([ms_state["rent_to_income"] * 100]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax2, np.array([ny_state["rent_to_income"] * 100]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax2, ms_puma["rent_to_income"].values, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax2, nyc_puma["rent_to_income"].values, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms2 = add_fit_line(ax2, ms_puma["rent_to_income"].values, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc2 = add_fit_line(ax2, nyc_puma["rent_to_income"].values, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(
        ax2, {"MS PUMAs": r_ms2, "NYC PUMAs": r_nyc2},
    )

    set_axis_labels(
        ax2,
        "Rent-to-Income Ratio (avg annual rent / avg renter income)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Housing Costs vs. Homeownership Measure Gap\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_RATIO_2,
    )
    add_legend(ax2, loc="upper left")
    save_figure(fig2, FileNames.PLOT_PUMA_RENT_VS_GAP, out_dir=PUMA_OUT_DIR)

    # ── Plot 3: Rent-to-Income 18-64 vs Gap (PUMA level) ──
    fig3, ax3 = setup_figure()

    style_scatter(
        ax3, np.array([ms_state["rent_to_income_18_64"] * 100]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax3, np.array([ny_state["rent_to_income_18_64"] * 100]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax3, ms_puma["rent_to_income_18_64"].values, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax3, nyc_puma["rent_to_income_18_64"].values, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms3 = add_fit_line(ax3, ms_puma["rent_to_income_18_64"].values, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc3 = add_fit_line(ax3, nyc_puma["rent_to_income_18_64"].values, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(
        ax3, {"MS PUMAs": r_ms3, "NYC PUMAs": r_nyc3},
    )

    set_axis_labels(
        ax3,
        "Rent-to-Income Ratio 18-64 (avg annual rent / avg renter income)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Housing Costs vs. Homeownership Measure Gap (Ages 18-64)\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_RATIO_2,
    )
    add_legend(ax3, loc="upper left")
    save_figure(fig3, FileNames.PLOT_PUMA_RENT_VS_GAP_18_64, out_dir=PUMA_OUT_DIR)

    # ── Plot 4: All-Adult Income vs Gap (PUMA level) ──
    fig4, ax4 = setup_figure()

    style_scatter(
        ax4, np.array([ms_state["avg_adult_income"]]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax4, np.array([ny_state["avg_adult_income"]]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax4, ms_puma["mean_adult_income"].values, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax4, nyc_puma["mean_adult_income"].values, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms4 = add_fit_line(ax4, ms_puma["mean_adult_income"].values, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc4 = add_fit_line(ax4, nyc_puma["mean_adult_income"].values, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(
        ax4, {"MS PUMAs": r_ms4, "NYC PUMAs": r_nyc4},
    )

    set_axis_labels(
        ax4,
        "Average Annual Personal Income (All Adults 18+)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Average Income vs. Homeownership Measure Gap\nMississippi State vs New York State vs PUMAs",
        x_format="$%.0f",
    )
    add_legend(ax4, loc="upper left")
    save_figure(fig4, FileNames.PLOT_PUMA_GAP_VS_INCOME, out_dir=PUMA_OUT_DIR)

    # ── Plot 5: Owner-Occ vs Gap (PUMA level) ──
    fig5, ax5 = setup_figure()

    style_scatter(
        ax5, np.array([ms_state["owner_occ_rate"]]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax5, np.array([ny_state["owner_occ_rate"]]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax5, ms_puma["owner_occ_rate"].values, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax5, nyc_puma["owner_occ_rate"].values, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms5 = add_fit_line(ax5, ms_puma["owner_occ_rate"].values, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc5 = add_fit_line(ax5, nyc_puma["owner_occ_rate"].values, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(
        ax5, {"MS PUMAs": r_ms5, "NYC PUMAs": r_nyc5},
    )

    set_axis_labels(
        ax5,
        "Owner-Occupancy Rate (% of occupied units)",
        "Owner-Occ − HPOP Rate (percentage points)",
        "Traditional Homeownership vs. Measure Gap\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_PCT,
    )
    add_legend(ax5, loc="upper left")
    save_figure(fig5, FileNames.PLOT_PUMA_GAP_VS_OWNER_OCC, out_dir=PUMA_OUT_DIR)

    # ── Plot 6: Owner-Occ vs Multifamily Share (PUMA level) ──
    fig6, ax6 = setup_figure()

    style_scatter(
        ax6, np.array([ms_state["pct_multifamily"]]), np.array([ms_state["owner_occ_rate"]]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax6, np.array([ny_state["pct_multifamily"]]), np.array([ny_state["owner_occ_rate"]]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax6, ms_puma["multifamily_share"].values, ms_puma["owner_occ_rate"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax6, nyc_puma["multifamily_share"].values, nyc_puma["owner_occ_rate"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms6 = add_fit_line(ax6, ms_puma["multifamily_share"].values, ms_puma["owner_occ_rate"].values, "ms_puma")
    r_nyc6 = add_fit_line(ax6, nyc_puma["multifamily_share"].values, nyc_puma["owner_occ_rate"].values, "nyc_puma")
    add_correlation_text(
        ax6, {"MS PUMAs": r_ms6, "NYC PUMAs": r_nyc6},
    )

    set_axis_labels(
        ax6,
        "Multifamily Share (% of occupied units)",
        "Owner-Occupancy Rate (% of occupied units)",
        "Homeownership vs. Multifamily Share\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_PCT,
    )
    add_legend(ax6, loc="upper right")
    save_figure(fig6, FileNames.PLOT_PUMA_OWNER_OCC_VS_MF, out_dir=PUMA_OUT_DIR)


if __name__ == "__main__":
    main()