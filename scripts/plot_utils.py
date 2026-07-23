#!/usr/bin/env python3
"""Shared utilities for plotting."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

from scripts.constants import PlotStyle, ROOT, OUT_DIR


def setup_figure(figsize: Tuple[float, float] = PlotStyle.FIG_SIZE) -> Tuple[plt.Figure, plt.Axes]:
    """Create a figure with standard styling."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.grid(True, alpha=PlotStyle.GRID_ALPHA)
    ax.axhline(y=0, color=PlotStyle.COLORS["zero_line"],
               linestyle=PlotStyle.ZERO_LINE_STYLE, alpha=PlotStyle.ZERO_LINE_ALPHA)
    return fig, ax


def style_scatter(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    color_key: str,
    label: str,
    size: float = PlotStyle.SCATTER_SIZE,
    zorder: int = PlotStyle.ZORDER_SCATTER,
    **kwargs
) -> None:
    """Add a styled scatter plot."""
    ax.scatter(
        x, y, s=size,
        c=PlotStyle.COLORS[color_key],
        edgecolors=PlotStyle.EDGE_COLOR,
        linewidths=PlotStyle.EDGE_WIDTH,
        zorder=zorder,
        label=label,
        **kwargs
    )


def add_fit_line(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    color_key: str,
    label: Optional[str] = None,
    x_pad: float = 0.5,
    **kwargs
) -> float:
    """
    Add a linear fit line and return correlation coefficient.

    Args:
        ax: Matplotlib axes
        x: X values
        y: Y values
        color_key: Key in PlotStyle.COLORS for the line color
        label: Optional label for legend
        x_pad: Padding for x range of fit line
        **kwargs: Additional arguments passed to plot()

    Returns:
        Correlation coefficient (r)
    """
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x.min() - x_pad, x.max() + x_pad, 100)

    ax.plot(
        x_line, p(x_line), "-",
        color=PlotStyle.COLORS[color_key],
        linewidth=PlotStyle.FIT_LINEWIDTH,
        alpha=PlotStyle.FIT_ALPHA,
        zorder=PlotStyle.ZORDER_FIT,
        label=label,
        **kwargs
    )

    return np.corrcoef(x, y)[0, 1]


def add_correlation_text(
    ax: plt.Axes,
    correlations: Dict[str, float],
    position: Tuple[float, float] = (0.98, 0.02),
    **kwargs
) -> None:
    """Add correlation coefficients as text box."""
    text = "\n".join([f"r = {r:.3f} ({label})" for label, r in correlations.items()])
    ax.text(
        position[0], position[1], text,
        transform=ax.transAxes,
        fontsize=PlotStyle.FONT_SIZES["correlation"],
        verticalalignment="bottom",
        horizontalalignment="right",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor=PlotStyle.COLORS["text_box"],
            edgecolor=PlotStyle.COLORS["text_box_edge"]
        ),
        **kwargs
    )


def annotate_points(
    ax: plt.Axes,
    df,
    x_col: str,
    y_col: str,
    label_col: str,
    fontsize: int = PlotStyle.FONT_SIZES["annotation"],
    **kwargs
) -> None:
    """Annotate scatter points with labels."""
    for _, row in df.iterrows():
        ax.annotate(
            row[label_col], (row[x_col], row[y_col]),
            fontsize=fontsize, ha="center", va="bottom",
            xytext=(0, 5), textcoords="offset points",
            **kwargs
        )


def set_axis_labels(
    ax: plt.Axes,
    xlabel: str,
    ylabel: str,
    title: str,
    x_format: Optional[str] = None,
    **kwargs
) -> None:
    """Set axis labels, title, and optional formatter."""
    ax.set_xlabel(xlabel, fontsize=PlotStyle.FONT_SIZES["axis_label"])
    ax.set_ylabel(ylabel, fontsize=PlotStyle.FONT_SIZES["axis_label"])
    ax.set_title(title, fontsize=PlotStyle.FONT_SIZES["title"],
                 fontweight=PlotStyle.FONT_WEIGHT_TITLE, **kwargs)

    if x_format:
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter(x_format))


def add_legend(ax: plt.Axes, **kwargs) -> None:
    """Add legend with standard styling."""
    ax.legend(fontsize=PlotStyle.FONT_SIZES["legend"], **kwargs)


def save_figure(
    fig: plt.Figure,
    filename: str,
    dpi: int = PlotStyle.DPI,
    out_dir: Optional[str] = None
) -> None:
    """Save figure with standard settings."""
    fig.tight_layout()
    if out_dir is None:
        out_dir = OUT_DIR
    path = out_dir / filename
    fig.savefig(path, dpi=dpi)
    print(f"Saved {path}")


def create_scatter_plot(
    x_data: Dict[str, np.ndarray],
    y_data: Dict[str, np.ndarray],
    color_keys: Dict[str, str],
    labels: Dict[str, str],
    xlabel: str,
    ylabel: str,
    title: str,
    x_format: str = PlotStyle.X_FORMAT_PCT,
    fit_colors: Optional[Dict[str, str]] = None,
    corr_labels: Optional[Dict[str, str]] = None,
    state_x: Optional[float] = None,
    state_y: Optional[float] = None,
    state_color: Optional[str] = None,
    state_label: Optional[str] = None,
    out_filename: Optional[str] = None,
    figsize: Tuple[float, float] = PlotStyle.FIG_SIZE,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a standardized scatter plot with multiple series, fit lines, and correlations.

    Args:
        x_data: Dict of series_name -> x values
        y_data: Dict of series_name -> y values
        color_keys: Dict of series_name -> PlotStyle.COLORS key
        labels: Dict of series_name -> legend label
        xlabel: X-axis label
        ylabel: Y-axis label
        title: Plot title
        x_format: X-axis format string
        fit_colors: Optional dict of series_name -> fit line color key
        corr_labels: Optional dict of series_name -> correlation label
        state_x, state_y: Optional state-level point coordinates
        state_color: Color key for state point
        state_label: Label for state point
        out_filename: If provided, save figure to this filename
        figsize: Figure size

    Returns:
        Tuple of (figure, axes)
    """
    fig, ax = setup_figure(figsize)

    correlations = {}

    # Plot each series
    for series_name in x_data:
        x = x_data[series_name]
        y = y_data[series_name]
        color = color_keys[series_name]
        label = labels[series_name]

        style_scatter(ax, x, y, color, label)

        # Fit line
        fit_color = fit_colors.get(series_name, color) if fit_colors else color
        corr = add_fit_line(ax, x, y, fit_color, x_pad=0.5)
        correlations[series_name] = corr

    # State-level point
    if state_x is not None and state_y is not None:
        style_scatter(
            ax, np.array([state_x]), np.array([state_y]),
            state_color, state_label,
            size=PlotStyle.STATE_SCATTER_SIZE,
            zorder=PlotStyle.ZORDER_STATE
        )

    # Correlation text
    if corr_labels:
        corr_dict = {corr_labels[k]: correlations[k] for k in correlations if k in corr_labels}
    else:
        corr_dict = {labels[k]: correlations[k] for k in correlations}

    add_correlation_text(ax, corr_dict)

    # Labels and legend
    set_axis_labels(ax, xlabel, ylabel, title, x_format=x_format)
    add_legend(ax)

    if out_filename:
        save_figure(fig, out_filename)

    return fig, ax