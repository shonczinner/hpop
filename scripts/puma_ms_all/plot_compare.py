#!/usr/bin/env python3
"""Plot housing form vs gap and rent-to-income: MS state, MS PUMAs, NYC PUMAs, NY state."""
import numpy as np
import matplotlib.pyplot as plt

from scripts.constants import (
    PlotStyle, FileNames, PUMA_OUT_DIR
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

    ms_adults_per_unit = ms_puma["n_adults"].values / ms_puma["n_occupied_units"].values
    nyc_adults_per_unit = nyc_puma["n_adults"].values / nyc_puma["n_occupied_units"].values

    # ── Plot 1: Rent-to-Income vs Gap (PUMA level) ──
    fig, ax = setup_figure()

    style_scatter(
        ax, np.array([ms_state["rent_to_income"] * 100]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax, np.array([ny_state["rent_to_income"] * 100]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax, ms_puma["rent_to_income"].values, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax, nyc_puma["rent_to_income"].values, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms = add_fit_line(ax, ms_puma["rent_to_income"].values, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc = add_fit_line(ax, nyc_puma["rent_to_income"].values, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(ax, {"MS PUMAs": r_ms, "NYC PUMAs": r_nyc})

    set_axis_labels(
        ax,
        "Rent-to-Income Ratio (avg annual rent / avg renter income)",
        "Owner-Occ \u2212 HPOP Rate (percentage points)",
        "Housing Costs vs. Homeownership Measure Gap\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_RATIO_2,
    )
    add_legend(ax, loc="upper left")
    save_figure(fig, FileNames.PLOT_PUMA_RENT_VS_GAP, out_dir=PUMA_OUT_DIR)

    # ── Plot 2: Multifamily Share vs Owner-Occupancy Rate (PUMA level) ──
    fig2, ax2 = setup_figure()

    rent_all = np.concatenate([ms_puma["mean_rent"].values, nyc_puma["mean_rent"].values])
    norm = plt.Normalize(vmin=rent_all.min(), vmax=rent_all.max())
    cmap = plt.cm.viridis

    ax2.scatter(
        ms_puma["multifamily_share"].values, ms_puma["owner_occ_rate"].values,
        c=ms_puma["mean_rent"].values, cmap=cmap, norm=norm,
        s=PlotStyle.SCATTER_SIZE, edgecolors=PlotStyle.EDGE_COLOR,
        linewidths=PlotStyle.EDGE_WIDTH, zorder=PlotStyle.ZORDER_SCATTER,
        label="Mississippi (PUMAs)",
    )
    ax2.scatter(
        nyc_puma["multifamily_share"].values, nyc_puma["owner_occ_rate"].values,
        c=nyc_puma["mean_rent"].values, cmap=cmap, norm=norm,
        s=PlotStyle.SCATTER_SIZE, edgecolors=PlotStyle.EDGE_COLOR,
        linewidths=PlotStyle.EDGE_WIDTH, zorder=PlotStyle.ZORDER_SCATTER,
        label="NYC (PUMAs)",
    )
    style_scatter(
        ax2, np.array([ms_state["pct_multifamily"]]), np.array([ms_state["owner_occ_rate"]]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax2, np.array([ny_state["pct_multifamily"]]), np.array([ny_state["owner_occ_rate"]]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )

    cbar = fig2.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax2)
    cbar.set_label("Avg Annual Rent ($)", fontsize=PlotStyle.FONT_SIZES["axis_label"])

    r_ms2 = add_fit_line(ax2, ms_puma["multifamily_share"].values, ms_puma["owner_occ_rate"].values, "ms_puma")
    r_nyc2 = add_fit_line(ax2, nyc_puma["multifamily_share"].values, nyc_puma["owner_occ_rate"].values, "nyc_puma")
    add_correlation_text(ax2, {"MS PUMAs": r_ms2, "NYC PUMAs": r_nyc2})

    set_axis_labels(
        ax2,
        "Multifamily Share (% of occupied units)",
        "Owner-Occupancy Rate (% of occupied units)",
        "Homeownership vs. Multifamily Share\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_PCT,
    )
    add_legend(ax2, loc="upper right")
    save_figure(fig2, FileNames.PLOT_PUMA_OWNER_OCC_VS_MF, out_dir=PUMA_OUT_DIR)

    # ── Plot 3: Adults per Home vs Gap (PUMA level) ──
    fig3, ax3 = setup_figure()

    style_scatter(
        ax3, np.array([ms_state["n_adults"] / ms_state["n_occupied_units"]]), np.array([ms_state_neg_gap]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax3, np.array([ny_state["n_adults"] / ny_state["n_occupied_units"]]), np.array([ny_state_neg_gap]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax3, ms_adults_per_unit, ms_puma["neg_gap"].values,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax3, nyc_adults_per_unit, nyc_puma["neg_gap"].values,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms3 = add_fit_line(ax3, ms_adults_per_unit, ms_puma["neg_gap"].values, "ms_puma")
    r_nyc3 = add_fit_line(ax3, nyc_adults_per_unit, nyc_puma["neg_gap"].values, "nyc_puma")
    add_correlation_text(ax3, {"MS PUMAs": r_ms3, "NYC PUMAs": r_nyc3})

    set_axis_labels(
        ax3,
        "Adults per Occupied Housing Unit",
        "Owner-Occ \u2212 HPOP Rate (percentage points)",
        "Household Size vs. Homeownership Measure Gap\nMississippi State vs New York State vs PUMAs",
    )
    add_legend(ax3, loc="upper right")
    save_figure(fig3, FileNames.PLOT_PUMA_GAP_VS_ADULTS_PER_UNIT, out_dir=PUMA_OUT_DIR)

    # ── Plot 4: Rent-to-Income vs Adults per Home (PUMA level) ──
    fig4, ax4 = setup_figure()

    style_scatter(
        ax4, np.array([ms_state["rent_to_income"] * 100]), np.array([ms_state["n_adults"] / ms_state["n_occupied_units"]]),
        "ms_state", "Mississippi (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax4, np.array([ny_state["rent_to_income"] * 100]), np.array([ny_state["n_adults"] / ny_state["n_occupied_units"]]),
        "ny_state", "New York (state)", size=PlotStyle.STATE_SCATTER_SIZE, zorder=5
    )
    style_scatter(
        ax4, ms_puma["rent_to_income"].values, ms_adults_per_unit,
        "ms_puma", "Mississippi (PUMAs)"
    )
    style_scatter(
        ax4, nyc_puma["rent_to_income"].values, nyc_adults_per_unit,
        "nyc_puma", "NYC (PUMAs)"
    )

    r_ms4 = add_fit_line(ax4, ms_puma["rent_to_income"].values, ms_adults_per_unit, "ms_puma")
    r_nyc4 = add_fit_line(ax4, nyc_puma["rent_to_income"].values, nyc_adults_per_unit, "nyc_puma")
    add_correlation_text(ax4, {"MS PUMAs": r_ms4, "NYC PUMAs": r_nyc4})

    set_axis_labels(
        ax4,
        "Rent-to-Income Ratio (avg annual rent / avg renter income)",
        "Adults per Occupied Housing Unit",
        "Rent-to-Income vs. Household Size\nMississippi State vs New York State vs PUMAs",
        x_format=PlotStyle.X_FORMAT_RATIO_2,
    )
    add_legend(ax4, loc="upper left")
    save_figure(fig4, FileNames.PLOT_PUMA_ADULTS_PER_UNIT_VS_RENT, out_dir=PUMA_OUT_DIR)


if __name__ == "__main__":
    main()
