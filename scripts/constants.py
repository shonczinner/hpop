"""Centralized constants for the HPOP analysis pipeline.

Single Source of Truth (SSOT) for all magic values:
- PUMS column names and codes
- BLD (building type) categories
- Geographic codes (FIPS, PUMAs)
- Output column definitions
- Plot styling
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/2024"
OUT_DIR = ROOT / "output"
PUMA_OUT_DIR = OUT_DIR / "puma"


class PUMS:
    SERIALNO = "SERIALNO"
    STATE = "STATE"
    RELSHIPP = "RELSHIPP"
    PWGTP = "PWGTP"
    AGEP = "AGEP"
    PINCP = "PINCP"
    TEN = "TEN"
    WGTP = "WGTP"
    TYPEHUGQ = "TYPEHUGQ"
    GRNTP = "GRNTP"
    BLD = "BLD"
    VALP = "VALP"
    PUMA = "PUMA"

    PERSON_COLS = [SERIALNO, STATE, RELSHIPP, PWGTP, AGEP, PINCP]
    HOUSING_COLS = [SERIALNO, STATE, TEN, WGTP, TYPEHUGQ, GRNTP, BLD, VALP]
    PUMA_PERSON_COLS = PERSON_COLS + [PUMA]
    PUMA_HOUSING_COLS = HOUSING_COLS + [PUMA]
    MERGE_KEYS = [SERIALNO, STATE]


class Codes:
    HOUSING_UNIT = 1

    OWNED_WITH_MORTGAGE = 1
    OWNED_FREE_CLEAR = 2
    RENTER_OCCUPIED = 3
    OWNER_OCCUPIED = {OWNED_WITH_MORTGAGE, OWNED_FREE_CLEAR}

    HOUSEHOLDER = 20
    SPOUSE = 21
    PARTNER = 22
    HOUSEHOLDER_SPOUSE_PARTNER = {HOUSEHOLDER, SPOUSE, PARTNER}

    MOBILE_HOME = 1
    SF_DETACHED = 2
    SF_ATTACHED = 3
    SMALL_MF_2 = 4
    SMALL_MF_3_4 = 5
    MED_MF_5_9 = 6
    MED_MF_10_19 = 7
    LARGE_MF_20_49 = 8
    LARGE_MF_50_PLUS = 9
    BOAT_RV_VAN = 10

    BLD_CATEGORIES = {
        "mobile": [MOBILE_HOME],
        "sf_detached": [SF_DETACHED],
        "sf_attached": [SF_ATTACHED],
        "multifamily": [SMALL_MF_2, SMALL_MF_3_4, MED_MF_5_9, MED_MF_10_19, LARGE_MF_20_49, LARGE_MF_50_PLUS],
        "other": [BOAT_RV_VAN],
    }

    SINGLE_FAMILY_CODES = BLD_CATEGORIES["sf_detached"] + BLD_CATEGORIES["sf_attached"]
    MULTIFAMILY_CODES = BLD_CATEGORIES["multifamily"]
    ADULT_AGE = 18


class Geo:
    FIPS_TO_STATE = {
        1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC",
        12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL", 18: "IN", 19: "IA", 20: "KS",
        21: "KY", 22: "LA", 23: "ME", 24: "MD", 25: "MA", 26: "MI", 27: "MN", 28: "MS",
        29: "MO", 30: "MT", 31: "NE", 32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY",
        37: "NC", 38: "ND", 39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC",
        46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV",
        55: "WI", 56: "WY",
    }
    STATE_TO_FIPS = {v: k for k, v in FIPS_TO_STATE.items()}
    PR_FIPS = 72
    MS_STATE_FIPS = 28
    NY_STATE_FIPS = 36

    NYC_PUMAS = {
        4103, 4104, 4107, 4108, 4109, 4110, 4111, 4112, 4121, 4165,
        4204, 4205, 4207, 4208, 4209, 4210, 4211, 4212, 4221, 4263,
        4301, 4302, 4303, 4304, 4305, 4306, 4307, 4308, 4309, 4310,
        4311, 4312, 4313, 4314, 4315, 4316, 4317, 4318,
        4401, 4402, 4403, 4404, 4405, 4406, 4407, 4408, 4409, 4410,
        4411, 4412, 4413, 4414,
        4501, 4502, 4503,
    }

    NYC_PUMA_NAMES = {
        4103: "Washington Heights",
        4104: "Inwood",
        4107: "Chelsea/Clinton",
        4108: "Greenwich Village",
        4109: "Central Harlem",
        4110: "East Harlem",
        4111: "Lower Manhattan",
        4112: "Morningside Heights",
        4121: "Hamilton Heights",
        4165: "Washington Heights South",
        4204: "Hunts Point/Longwood",
        4205: "Melrose",
        4207: "Morrisania",
        4208: "Concourse",
        4209: "Highbridge",
        4210: "Kingsbridge",
        4211: "Riverdale",
        4212: "Pelham Parkway",
        4221: "Eastchester",
        4263: "Fordham",
        4301: "Park Slope",
        4302: "Sunset Park",
        4303: "Borough Park",
        4304: "Flatbush",
        4305: "Crown Heights",
        4306: "Williamsburg",
        4307: "Greenpoint",
        4308: "Bushwick",
        4309: "East New York",
        4310: "Canarsie",
        4311: "Bay Ridge",
        4312: "Bensonhurst",
        4313: "Bath Beach",
        4314: "Coney Island",
        4315: "Gravesend",
        4316: "Flatlands",
        4317: "New Lots",
        4318: "Bergen Beach",
        4401: "Astoria",
        4402: "Long Island City",
        4403: "Jackson Heights",
        4404: "Elmhurst",
        4405: "Corona",
        4406: "Flushing",
        4407: "Forest Hills",
        4408: "Ridgewood",
        4409: "Rego Park",
        4410: "Kew Gardens",
        4411: "Woodhaven",
        4412: "Jamaica",
        4413: "Howard Beach",
        4414: "Ozone Park",
        4501: "St. George",
        4502: "New Dorp",
        4503: "Tottenville",
    }

    MS_PUMA_NAMES = {
        "00100": "North Region",
        "00200": "Northeast Region",
        "00300": "North Central Region",
        "00400": "Northeast Delta Region",
        "00500": "East Central Region",
        "00600": "Central West Region",
        "00700": "South Delta Region",
        "00800": "Southwest Region",
        "00900": "Central Region - Madison & Rankin Counties",
        "01001": "Central Region - Jackson City",
        "01101": "Central Region - Jackson (East & Central)",
        "01300": "Central Region - Rankin & Simpson Counties",
        "01400": "Pine Belt Region",
        "01500": "Gulf Coast Region - Jackson County",
        "01600": "Gulf Coast Region - Harrison & Hancock Counties",
        "01700": "Southwest Pine Region",
        "01800": "Southern Region",
        "01900": "Southeast Pine Region",
        "02001": "Gulf Coast Region - Harrison County West",
        "02002": "Gulf Coast Region - Harrison County East",
        "02100": "Gulf Coast Region - Jackson County",
    }

    VALID_STATE_FIPS = set(FIPS_TO_STATE.keys())


class OutputColumns:
    STATE_LEVEL = [
        "state",
        "hpop",
        "owner_occ_rate",
        "gap_pp",
        "rent_to_income",
        "rent_to_income_18_64",
        "price_to_income",
        "avg_annual_rent",
        "avg_personal_income",
        "avg_annual_rent_18_64",
        "avg_renter_income_18_64",
        "avg_adult_income",
        "avg_property_value",
        "avg_owner_income",
        "pct_multifamily",
        "pct_singlefamily",
        "sf_detached",
        "sf_attached",
        "mobile",
    ]

    PUMA_LEVEL = [
        "state",
        "puma",
        "region",
        "name",
        "n_adults",
        "n_occupied_units",
        "hpop",
        "owner_occ_rate",
        "gap_pp",
        "mean_rent",
        "mean_rent_18_64",
        "rent_to_income",
        "rent_to_income_18_64",
        "mean_adult_income",
        "sf_detached_share",
        "multifamily_share",
    ]


class PlotStyle:
    FIG_SIZE = (10, 7)
    DPI = 150
    COLORS = {
        "ms_state": "#FFA726",
        "ms_puma": "#FF8C00",
        "ny_state": "#1B5E20",
        "nyc_puma": "#2E7D32",
        "scatter_main": "#D4A843",
        "fit_line_ms": "#FF8C00",
        "fit_line_nyc": "#2E7D32",
        "fit_line": "#888888",
        "grid": "#CCCCCC",
        "zero_line": "gray",
        "text_box": "white",
        "text_box_edge": "#CCCCCC",
        "annotation": "#333333",
    }
    SCATTER_SIZE = 50
    STATE_SCATTER_SIZE = 200
    EDGE_COLOR = "#333333"
    EDGE_WIDTH = 0.5
    ZORDER_SCATTER = 3
    ZORDER_STATE = 5
    ZORDER_FIT = 2
    FIT_LINEWIDTH = 1.5
    FIT_ALPHA = 0.6
    ZERO_LINE_STYLE = "--"
    ZERO_LINE_ALPHA = 0.5
    GRID_ALPHA = 0.3
    FONT_SIZES = {
        "title": 13,
        "axis_label": 11,
        "tick_label": 10,
        "annotation": 7,
        "correlation": 10,
        "legend": 10,
    }
    FONT_WEIGHT_TITLE = "bold"
    X_FORMAT_PCT = "%.0f"
    X_FORMAT_RATIO_2 = "%.2f"
    X_FORMAT_RATIO_1 = "%.1f"


class FileNames:
    STATE_CSV = "hpop_by_state_2024.csv"
    STATE_MD = "results.md"
    MS_PUMA_CSV = "ms_puma_metrics.csv"
    NYC_PUMA_CSV = "nyc_puma_metrics.csv"
    PUMA_MD = "puma_results.md"
    PLOT_GAP_RENT = "gap_vs_rent_to_income.png"
    PLOT_GAP_RENT_18_64 = "gap_vs_rent_to_income_18_64.png"
    PLOT_GAP_PRICE = "gap_vs_price_to_income.png"
    PLOT_MF_VS_GAP = "compare_multifamily_vs_gap.png"
    PLOT_PUMA_RENT_VS_GAP = "puma_rent_to_income_vs_gap.png"
    PLOT_PUMA_RENT_VS_GAP_18_64 = "puma_rent_to_income_18_64_vs_gap.png"
    PLOT_STATE_MF_VS_GAP = "state_multifamily_vs_gap.png"
    PLOT_GAP_VS_INCOME = "gap_vs_adult_income.png"
    PLOT_GAP_VS_OWNER_OCC = "gap_vs_owner_occ.png"
    PLOT_OWNER_OCC_VS_MF = "owner_occ_vs_multifamily.png"
    PLOT_PUMA_GAP_VS_OWNER_OCC = "puma_gap_vs_owner_occ.png"
    PLOT_PUMA_OWNER_OCC_VS_MF = "puma_owner_occ_vs_multifamily.png"
    PLOT_PUMA_GAP_VS_INCOME = "puma_gap_vs_adult_income.png"
