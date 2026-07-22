import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/2024"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

# ── Load person data (concatenate a + b splits) ────────
print("Loading person data...")
person = pd.concat([
    pd.read_csv(DATA / "psam_pusa.csv", usecols=["SERIALNO", "STATE", "RELSHIPP", "PWGTP", "AGEP", "PINCP"],
                dtype={"SERIALNO": str}),
    pd.read_csv(DATA / "psam_pusb.csv", usecols=["SERIALNO", "STATE", "RELSHIPP", "PWGTP", "AGEP", "PINCP"],
                dtype={"SERIALNO": str}),
], ignore_index=True)

# ── Load housing data (concatenate a + b splits) ───────
print("Loading housing data...")
housing = pd.concat([
    pd.read_csv(DATA / "psam_husa.csv", usecols=["SERIALNO", "STATE", "TEN", "WGTP", "TYPEHUGQ", "GRNTP", "BLD"],
                dtype={"SERIALNO": str}),
    pd.read_csv(DATA / "psam_husb.csv", usecols=["SERIALNO", "STATE", "TEN", "WGTP", "TYPEHUGQ", "GRNTP", "BLD"],
                dtype={"SERIALNO": str}),
], ignore_index=True)

# ══════════════════════════════════════════════════════════
# OWNER-OCCUPANCY RATE (from housing data only)
# ══════════════════════════════════════════════════════════
print("Computing owner-occupancy rate...")
hu = housing[(housing["TYPEHUGQ"] == 1) & housing["TEN"].notna()].copy()
hu["owner_occ"] = hu["TEN"].isin([1, 2])

ownocc_by_state = hu.groupby("STATE").apply(lambda g: pd.Series({
    "owner_occ_rate": (g["WGTP"] * g["owner_occ"]).sum() / g["WGTP"].sum() * 100,
})).reset_index()

# ══════════════════════════════════════════════════════════
# HPOP (from person data, merged with housing for tenure)
# ══════════════════════════════════════════════════════════
print("Computing HPOP...")
df = person.merge(housing[["SERIALNO", "STATE", "TEN", "TYPEHUGQ", "BLD"]], on=["SERIALNO", "STATE"], how="left")

df = df[(df["TYPEHUGQ"] == 1) & (df["AGEP"] >= 18)].copy()
df["owner_occ"] = df["TEN"].isin([1, 2])
df["is_homeowner"] = df["owner_occ"] & df["RELSHIPP"].isin([20, 21, 22])

hpop_by_state = df.groupby("STATE").apply(lambda g: pd.Series({
    "hpop": (g["PWGTP"] * g["is_homeowner"]).sum() / g["PWGTP"].sum() * 100,
})).reset_index()

# ══════════════════════════════════════════════════════════
# RENT-TO-INCOME RATIO (adult renters only)
# ══════════════════════════════════════════════════════════
print("Computing rent-to-income ratio...")
renters = person.merge(
    housing[["SERIALNO", "STATE", "TEN", "TYPEHUGQ", "GRNTP"]],
    on=["SERIALNO", "STATE"], how="left"
)
# TEN=3 = rented, GRNTP = gross monthly rent, PINCP = annual personal income
renters = renters[
    (renters["TYPEHUGQ"] == 1) &
    (renters["TEN"] == 3) &
    (renters["AGEP"] >= 18) &
    (renters["GRNTP"].notna()) &
    (renters["GRNTP"] > 0) &
    (renters["PINCP"].notna())
].copy()

renters["annual_rent"] = renters["GRNTP"] * 12

rent_income_by_state = renters.groupby("STATE").apply(lambda g: pd.Series({
    "avg_annual_rent": (g["PWGTP"] * g["annual_rent"]).sum() / g["PWGTP"].sum(),
    "avg_personal_income": (g["PWGTP"] * g["PINCP"]).sum() / g["PWGTP"].sum(),
})).reset_index()
rent_income_by_state["rent_to_income"] = (
    rent_income_by_state["avg_annual_rent"] / rent_income_by_state["avg_personal_income"]
)

# ══════════════════════════════════════════════════════════
# HOUSING FORM (from person data merged with housing BLD)
# ══════════════════════════════════════════════════════════
print("Computing housing form shares...")
# BLD: 1=mobile, 2=SF-detached, 3=SF-attached, 4-5=small MF (2-4 units),
#      6-7=medium MF (5-19 units), 8-9=large MF (20+ units), 10=other
bld_map = {1: "mobile", 2: "sf_detached", 3: "sf_attached",
           4: "small_mf", 5: "small_mf", 6: "med_mf", 7: "med_mf",
           8: "large_mf", 9: "large_mf", 10: "other"}
df["housing_form"] = df["BLD"].map(bld_map)

adults = df[(df["AGEP"] >= 18) & df["housing_form"].notna()].copy()

form_shares = adults.groupby(["STATE", "housing_form"]).apply(
    lambda g: pd.Series({"pop": g["PWGTP"].sum()})
).reset_index()

total_by_state = adults.groupby("STATE")["PWGTP"].sum().reset_index(name="total_pop")
form_shares = form_shares.merge(total_by_state, on="STATE")
form_shares["pct"] = form_shares["pop"] / form_shares["total_pop"] * 100

# Pivot to wide: one column per housing form
form_wide = form_shares.pivot(index="STATE", columns="housing_form", values="pct").fillna(0).reset_index()

# Total multifamily (small + medium + large)
form_wide["pct_multifamily"] = form_wide.get("small_mf", 0) + form_wide.get("med_mf", 0) + form_wide.get("large_mf", 0)
form_wide["pct_singlefamily"] = form_wide.get("sf_detached", 0) + form_wide.get("sf_attached", 0)

print(form_wide[["STATE", "pct_multifamily", "pct_singlefamily", "sf_detached", "sf_attached",
                  "small_mf", "med_mf", "large_mf", "mobile"]].round(1).to_string(index=False))

# ══════════════════════════════════════════════════════════
# COMBINE & OUTPUT
# ══════════════════════════════════════════════════════════
state = hpop_by_state.merge(ownocc_by_state, on="STATE", how="outer")
state = state.merge(rent_income_by_state[["STATE", "rent_to_income", "avg_annual_rent", "avg_personal_income"]],
                    on="STATE", how="left")
state = state.merge(form_wide[["STATE", "pct_multifamily", "pct_singlefamily", "sf_detached", "sf_attached",
                               "small_mf", "med_mf", "large_mf", "mobile"]],
                    on="STATE", how="left")
state["gap_pp"] = state["hpop"] - state["owner_occ_rate"]

# Exclude Puerto Rico
state = state[state["STATE"] != 72].copy()

# FIPS to abbreviation
fips = {1:"AL",2:"AK",4:"AZ",5:"AR",6:"CA",8:"CO",9:"CT",10:"DE",11:"DC",
        12:"FL",13:"GA",15:"HI",16:"ID",17:"IL",18:"IN",19:"IA",20:"KS",
        21:"KY",22:"LA",23:"ME",24:"MD",25:"MA",26:"MI",27:"MN",28:"MS",
        29:"MO",30:"MT",31:"NE",32:"NV",33:"NH",34:"NJ",35:"NM",36:"NY",
        37:"NC",38:"ND",39:"OH",40:"OK",41:"OR",42:"PA",44:"RI",45:"SC",
        46:"SD",47:"TN",48:"TX",49:"UT",50:"VT",51:"VA",53:"WA",54:"WV",
        55:"WI",56:"WY"}
state["state"] = state["STATE"].map(fips)

# Save
out_cols = ["state", "hpop", "owner_occ_rate", "gap_pp", "rent_to_income", "avg_annual_rent", "avg_personal_income",
            "pct_multifamily", "pct_singlefamily", "sf_detached", "sf_attached", "small_mf", "med_mf", "large_mf", "mobile"]
state[out_cols].to_csv(OUT / "hpop_by_state_2024.csv", index=False)

# Print
print(state[["state", "hpop", "owner_occ_rate", "gap_pp", "rent_to_income"]].sort_values("hpop", ascending=False).to_string(index=False))

# National
nat_hpop = (df["PWGTP"] * df["is_homeowner"]).sum() / df["PWGTP"].sum() * 100
nat_ownocc = (hu["WGTP"] * hu["owner_occ"]).sum() / hu["WGTP"].sum() * 100
nat_rent = (renters["PWGTP"] * renters["annual_rent"]).sum() / renters["PWGTP"].sum()
nat_income = (renters["PWGTP"] * renters["PINCP"]).sum() / renters["PWGTP"].sum()
print(f"\nNational HPOP: {nat_hpop:.1f}%")
print(f"National Owner-Occ: {nat_ownocc:.1f}%")
print(f"National Gap: {nat_hpop - nat_ownocc:.1f} pp")
print(f"National Rent-to-Income: {nat_rent/nat_income:.3f}")
