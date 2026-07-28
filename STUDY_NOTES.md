# Study: Illegal Parking at Bus Stops — Impact on On-Time Performance (OTP)

Working notes and confirmed inputs for the study. Nothing here is a result
yet — this file records the base data and parameters agreed so far, so the
analysis is reproducible once the GTFS files are in this repository.

## Problem statement

Private cars, taxis and limousines stopping in bus laybys cause:

1. **OTP degradation** — buses are delayed entering the stop, or must
   re-approach / queue.
2. **Safety & accessibility incidents** — drivers are forced to board/alight
   passengers in the live traffic lane (photo evidence on file, 28 Jul 2026,
   white Lexus ES blocking a layby while an RTA bus serves the road).

## Base observation data (confirmed: ONE DAY, AM peak only)

Source: field observation, **07:00–10:00, single day**, 11 locations.
"Cases" = instances of a taxi/limousine/private car occupying the bus layby.

| # | Location | Routes serving | Cases (3 h) |
|---|----------|----------------|-------------|
| 1 | Naif Intersection | 10, 13A, 13D, 25, 27, 64 | 5 |
| 2 | Burj Nahar | 10, 13A, 13D, C01, C04 | 5 |
| 3 | Al Jafliya | 21A, C26, 88, F09 | 6 |
| 4 | Emirates Tower | 29, 98E, F11, F28 | 3 |
| 5 | Al Khail Mall | F15, F16, F17 | 2 |
| 6 | Al Hana Center | 14, 15, 28, 93, C01, C10, X02 | 5 |
| 7 | Burjuman Bus Stop | 21B, 29, 44, 61 | 7 |
| 8 | Sharaf DG Metro | C01, C03, C18, 61 | 8 |
| 9 | Al Rigga Metro Bus Stop | C09, 77 | 5 |
| 10 | Salah Al Din Metro Bus Stop | 13A, C28, 10, 43 | 4 |
| 11 | Business Bay (all stops) | 51, F19A, F19B, F41 | 10 |
| | **Total** | | **60** |

## Agreed study parameters

| Parameter | Value | Status |
|-----------|-------|--------|
| Sample period | 1 day, 07:00–10:00 (AM peak) | Confirmed |
| Average blockage duration per case | **30 seconds** | Confirmed by ops (to be sanity-checked against runtime data) |
| OTP definition | On time = departure between **1 min early and 5 min late** (early < −1 min, late > +5 min) | Confirmed |
| Runtime report | 22 Jul 2026, routes above | Received — `data/Runtime_2026-07-22.xlsx` (75,780 AVL stop records, 38 routes, 2,999 trips) |
| Parking-violation records near stops | Not available | Confirmed unavailable |
| PM peak observations | Not available — to be assumed from AM profile | Assumption |

## Data pipeline

GTFS source: Hive database `pta_wojhati_raw` (tables `wojhati_gtfs_*`) in the
Dataiku project **RTABUSSCN**. The webapp in [`dataiku_webapp/`](dataiku_webapp/)
exports those tables as standard GTFS text files / `gtfs.zip`, which will then
be committed to this repository under `gtfs/`.

## Status

The study is built — see **[STUDY.md](STUDY.md)** for the full write-up,
`analysis/runtime_analysis.py` for the reproducible computation, and
`analysis/parking_otp_impact_model.xlsx` for the adjustable scenario model.

Remaining step: network-wide affected-stop identification, which needs the
GTFS export from `dataiku_webapp/` (risk-profiling every stop on route
count, peak throughput and metro/mall adjacency).
