#!/usr/bin/env python3
"""Download 2024 ACS 1-Year PUMS data and Minneapolis Fed HPOP data."""
import urllib.request
import zipfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/2024"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DOWNLOADS = [
    {
        "url": "https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_pus.zip",
        "name": "csv_pus.zip",
    },
    {
        "url": "https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_hus.zip",
        "name": "csv_hus.zip",
    },
    {
        "url": "https://github.com/frb-mpls-cde/hpop/raw/refs/heads/main/data/hpop_current.xlsx",
        "name": "mfed_hpop.xlsx",
    },
]


def download(url: str, dest: Path) -> None:
    print(f"Downloading {dest.name}...")
    urllib.request.urlretrieve(url, dest)


def main() -> None:
    for item in DOWNLOADS:
        dest = DATA_DIR / item["name"]
        download(item["url"], dest)

        if dest.suffix == ".zip":
            print(f"Extracting {dest.name}...")
            with zipfile.ZipFile(dest) as zf:
                zf.extractall(DATA_DIR)
            dest.unlink()
            print(f"Removed {dest.name}")

    print("\nDone. Files in data/2024/:")
    for f in sorted(DATA_DIR.iterdir()):
        size = f.stat().st_size
        if size > 1_000_000_000:
            print(f"  {f.name:30s}  {size / 1e9:.1f} GB")
        elif size > 1_000_000:
            print(f"  {f.name:30s}  {size / 1e6:.0f} MB")
        else:
            print(f"  {f.name:30s}  {size / 1e3:.0f} KB")


if __name__ == "__main__":
    main()
