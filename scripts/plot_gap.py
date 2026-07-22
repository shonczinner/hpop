import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

df = pd.read_csv(OUT / "hpop_by_state_2024.csv")

fig, ax = plt.subplots(figsize=(10, 7))

df["neg_gap"] = -df["gap_pp"]

ax.scatter(df["rent_to_income"], df["neg_gap"], s=50, c="#D4A843", edgecolors="#333", linewidths=0.5, zorder=3)

for _, row in df.iterrows():
    ax.annotate(row["state"], (row["rent_to_income"], row["neg_gap"]),
                fontsize=7, ha="center", va="bottom", xytext=(0, 5),
                textcoords="offset points")

# Trend line
z = np.polyfit(df["rent_to_income"], df["neg_gap"], 1)
p = np.poly1d(z)
x_line = np.linspace(df["rent_to_income"].min() - 0.01, df["rent_to_income"].max() + 0.01, 100)
ax.plot(x_line, p(x_line), "--", color="#888", linewidth=1, zorder=2)

corr = df["rent_to_income"].corr(df["neg_gap"])
ax.text(0.02, 0.98, f"r = {corr:.3f}", transform=ax.transAxes,
        fontsize=10, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#ccc"))

ax.set_xlabel("Rent-to-Income Ratio (avg annual rent / avg renter income)", fontsize=11)
ax.set_ylabel("Owner-Occ Rate − HPOP (percentage points)", fontsize=11)
ax.set_title("Housing Costs vs. Homeownership Measure Gap by State (2024)", fontsize=13, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
ax.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig(OUT / "gap_vs_rent_to_income.png", dpi=150)
print(f"Saved {OUT / 'gap_vs_rent_to_income.png'}")

# ── Plot 2: Gap vs Price-to-Income ───────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 7))

ax2.scatter(df["price_to_income"], df["neg_gap"], s=50, c="#D4A843", edgecolors="#333", linewidths=0.5, zorder=3)

for _, row in df.iterrows():
    ax2.annotate(row["state"], (row["price_to_income"], row["neg_gap"]),
                fontsize=7, ha="center", va="bottom", xytext=(0, 5),
                textcoords="offset points")

z2 = np.polyfit(df["price_to_income"], df["neg_gap"], 1)
p2 = np.poly1d(z2)
x2 = np.linspace(df["price_to_income"].min() - 0.5, df["price_to_income"].max() + 0.5, 100)
ax2.plot(x2, p2(x2), "--", color="#888", linewidth=1, zorder=2)

corr2 = df["price_to_income"].corr(df["neg_gap"])
ax2.text(0.02, 0.98, f"r = {corr2:.3f}", transform=ax2.transAxes,
        fontsize=10, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#ccc"))

ax2.set_xlabel("Price-to-Income Ratio (avg property value / avg owner income)", fontsize=11)
ax2.set_ylabel("Owner-Occ Rate − HPOP (percentage points)", fontsize=11)
ax2.set_title("Home Values vs. Homeownership Measure Gap by State (2024)", fontsize=13, fontweight="bold")
ax2.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
ax2.grid(True, alpha=0.3)

fig2.tight_layout()
fig2.savefig(OUT / "gap_vs_price_to_income.png", dpi=150)
print(f"Saved {OUT / 'gap_vs_price_to_income.png'}")


