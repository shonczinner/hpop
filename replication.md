# HPOP & OOR Replication

Exact specification for replicating the Minneapolis Fed's HPOP and OOR estimates using ACS 2024 1-year PUMS microdata.

## Data Source

**Survey:** ACS 2024 1-Year PUMS

**States:** All 50 states + DC (51 total)

**Files:** Census Bureau CSV extracts (`psam_pusa/b.csv` for persons, `psam_husa/b.csv` for housing)

**Variables:**

| Variable | File | Description |
|----------|------|-------------|
| `SERIALNO` | Both | Housing unit / group quarters serial number |
| `STATE` | Both | State FIPS code |
| `PUMA` | Person | PUMA code |
| `SPORDER` | Person | Person line number within household |
| `AGEP` | Person | Age |
| `TEN` | Housing | Tenure (1=owned w/ mortgage, 2=owned free & clear, 3=rented, 4=occupied w/o rent) |
| `RELSHIPP` | Person | Relationship to reference person |
| `PWGTP` | Person | Person weight |
| `WGTP` | Housing | Housing unit weight |
| `PINCP` | Person | Personal income |
| `POVPIP` | Person | Income-to-poverty ratio |
| `TYPEHUGQ` | Housing | Type of unit (1=housing unit, 2-3=group quarters) |

## HPOP (Homeowner Population Rate)

**Denominator:** All adults age 18+, weighted by `PWGTP`. No group-quarters filter — the denominator includes the full adult population (housing units + group quarters).

```
n_adults = sum(PWGTP where AGEP >= 18)
```

**Numerator:** Homeowners (adults 18+ in owner-occupied units), weighted by `PWGTP`.

A person is counted as a homeowner if ALL of the following hold:
- Age >= 18
- Lives in an owner-occupied unit: `TEN = 1` or `TEN = 2`
- Relationship to reference person is one of:

| RELSHIPP | ACS 2024 Label | Notes |
|----------|----------------|-------|
| 20 | Reference person | The householder |
| 21 | Spouse | Married partner of reference person |
| 22 | Unmarried partner | Cohabiting partner |
| 23 | Biological son or daughter | Adult children living with parents |
| 24 | Adopted son or daughter | Adopted adult children |

Notes on RELSHIPP codes:
- Code 22 in the 2024 ACS PUMS is **Unmarried partner**, NOT "Biological son or daughter." Some documentation conflates these. The Fed's HPOP definition includes unmarried partners as homeowners.
- Codes 23 (biological child) and 24 (adopted child) are included in the Fed's definition despite some simplified descriptions only mentioning "spouse or unmarried partner." Including children increases HPOP by ~0.3pp.

```
n_homeowners = sum(PWGTP where AGEP >= 18
                   and TEN in {1, 2}
                   and RELSHIPP in {20, 21, 22, 23, 24})
```

**Group quarters handling:** Persons in group quarters (TYPEHUGQ != 1 or no matching housing record) are included in the denominator (they are adults) but excluded from the numerator (they have no TEN value). Excluding GQ persons from the denominator inflates HPOP by ~1.6pp, so this is a critical detail.

**Formula:**

```
HPOP = n_homeowners / n_adults
```

## OOR (Owner-Occupancy Rate)

Computed at the housing-unit level using `WGTP` (housing weight). The housing file already has one row per unique `SERIALNO`, so no deduplication is needed. Only occupied units are considered (TEN is not null).

**Denominator:** All occupied housing units

```
n_occupied_homes = sum(WGTP where TEN is not null)
```

**Numerator:** Owner-occupied housing units

```
n_owned_homes = sum(WGTP where TEN in {1, 2})
```

**Formula:**

```
OOR = n_owned_homes / n_occupied_homes
```

## Filters Summary

| Filter | HPOP | OOR |
|--------|------|-----|
| Age >= 18 | Numerator & denominator | N/A |
| Group quarters in denominator | Yes | N/A |
| One row per SERIALNO | N/A | Housing file is already 1-per-SERIALNO |
| Weight | `PWGTP` (person weight) | `WGTP` (housing weight) |
| `TEN` 1 or 2 (owner-occupied) | Numerator | Numerator |
| `RELSHIPP` 20-24 | Numerator | N/A |

## Geographic Levels

- **State level:** Group by `STATE` FIPS code.
- **PUMA level:** Group by concatenated `STATE` + `PUMA`.

Both levels use the same `n_adults` / `n_homeowners` / `n_owned_homes` / `n_occupied_homes` logic, just grouped differently.

## State-Level Validation

Fed reference data from:

```
https://raw.githubusercontent.com/frb-mpls-cde/hpop/main/data/hpop_current.xlsx
```

Sheet: `hpop_oown_state`, filtered to `year == 2024`. Mapping from `fips` column to state abbreviation via lookup table.

Comparison columns: `hpop` (Fed HPOP %), `ownocc` (Fed OOR %).

Convert our rates to percentage points (multiply by 100) before comparing.

## Income Extension

Median personal income (`PINCP`) by tenure, weighted by `PWGTP`:

- **Homeowner income:** Weighted median of `PINCP` for persons matching HPOP homeowner filter.
- **Renter income:** Weighted median of `PINCP` for adults 18+ with `TEN` in {3, 4}.

```
is_homeowner = AGEP >= 18 and TEN in {1, 2} and RELSHIPP in {20, 21, 22, 23, 24}
is_renter = AGEP >= 18 and TEN in {3, 4}

homeowner_median_income = weightedMedian(PINCP[is_homeowner], weight = PWGTP)
renter_median_income = weightedMedian(PINCP[is_renter], weight = PWGTP)
```

Weighted median: sort values ascending, compute cumulative weight, find value where cumulative weight crosses 50% of total weight.

## Population Density

```
density_km2 = n_adults / (ALAND20 / 1e6)
```

Where `ALAND20` is PUMA land area in square meters (from Census TIGER 2020 PUMA boundaries). `n_adults` is the HPOP denominator (all adults 18+ in the PUMA).

## Methodological Findings

### Key factors to match Fed estimates exactly (r=1.0000, MAE < 0.05pp)

1. **RELSHIPP must be {20, 21, 22, 23, 24}.** The Fed's published definition includes biological children (23) and adopted children (24) as homeowners, not just householder/spouse/unmarried partner.

2. **Group quarters must be in the denominator.** The HPOP denominator is ALL adults 18+ — not just those in housing units. Excluding GQ inflates HPOP by ~1.6pp.

3. **OOR uses the housing file directly** (one row per SERIALNO). No deduplication needed. The housing weight (`WGTP`) is the correct weight.
