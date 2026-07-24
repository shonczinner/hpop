#!/usr/bin/env python3
"""Main pipeline: download data, compute metrics, generate plots."""
import subprocess
import sys

from scripts.constants import ROOT, DATA_DIR


def run(module: str) -> None:
    """Run a script as a module and exit on failure."""
    print(f"\n{'='*60}")
    print(f"Running: {module}")
    print('='*60)
    result = subprocess.run(
        [sys.executable, "-m", module],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print(f"\nFAILED: {module}")
        sys.exit(1)


def main() -> None:
    # 1. Download data (~3GB, skip if already exists)
    if not DATA_DIR.exists() or not any(DATA_DIR.glob("psam_pusa.csv")):
        run("scripts.download_data")
    else:
        print("Data already exists, skipping download.")

    # 2. State-level HPOP analysis
    run("scripts.hpop_state_2024")

    # 3. State-level plots
    run("scripts.plot_gap")

    # 4. Results markdown
    run("scripts.results_to_md")

    # 5. Mississippi PUMA analysis
    run("scripts.puma_ms_all.puma_analysis")

    # 6. Mississippi vs NYC comparison plots
    run("scripts.puma_ms_all.plot_compare")

    # 7. PUMA results markdown
    run("scripts.puma_ms_all.puma_results_to_md")

    print("\n" + "="*60)
    print("Pipeline complete! Outputs in output/")
    print("="*60)


if __name__ == "__main__":
    main()