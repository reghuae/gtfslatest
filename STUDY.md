# Impact of Illegal Parking at Bus Stops on Bus On-Time Performance

**Dubai bus network — evidence study based on field observations (11 locations)
and AVL runtime data (22 July 2026)**

---

## 1. Executive summary

Private cars, taxis and limousines routinely occupy bus laybys at busy stops.
A one-day field survey (07:00–10:00) at 11 high-demand locations recorded
**60 blocked-layby cases in three hours** — roughly **1 in 21 AM-peak bus
arrivals** at those stops met an obstructed layby. The blockage has two
effects:

1. **On-time performance (OTP)** — the bus loses time queuing, re-approaching,
   or serving the stop from the traffic lane.
2. **Safety & accessibility** — drivers are forced to board/alight passengers
   in the live traffic lane (photo evidence on file, 28 Jul 2026).

Extrapolated to both daily peaks across a working year, the 11 surveyed
locations alone generate an estimated **≈ 30,000 obstructed bus arrivals per
year** (range 27,000–36,600). Using the empirical schedule-deviation
distribution from the 22 July AVL data (75,780 stop records, 2,999 trips,
38 routes) and RTA's OTP window (−1 min early / +5 min late):

| Scenario (delay per obstructed arrival) | Extra late trips / year | OTP loss on affected peak trips | OTP loss across all 38 routes |
|---|---|---|---|
| 30 s (operations estimate) | ≈ 780 | **−0.29 pp** | −0.07 pp |
| 60 s (queue + re-approach) | ≈ 1,900 | **−0.70 pp** | −0.17 pp |

Scaled network-wide with a three-tier risk model (Section 8) — 112
High-sensitivity stops matching the surveyed profile, plus the next 400
(Medium) and following 400 (Low) stops by peak throughput — the estimate
reaches **≈ 346,000 blocked-layby events per year across 912 stops carrying
76 % of all peak bus arrivals**, costing **≈ 2,900 bus-hours of direct delay
and 0.35–0.85 percentage points of peak OTP** network-wide. The stronger
case for enforcement is the combination: measurable OTP erosion **plus**
hundreds of thousands of annual passenger-safety exposures where boarding
happens in a live traffic lane.

Camera enforcement turns the problem into a self-funding programme
(Sections 10–11): at an AED 200 fine, detected violations yield **≈ AED 46 M
in year 1**, declining by design as deterrence works. The recommended hybrid
— **fixed cameras at the 512 High + Medium stops (5-yr NPV +79 M AED,
payback < 1 year) plus a 20–30 unit portable fleet for the long tail
(NPV +8–13 M)** — pays for itself within the first year and delivers the
OTP and safety gains as the permanent return.

---

## 2. Data sources

| Source | Content | Status |
|---|---|---|
| Field survey | 11 locations, blocked-layby cases, 07:00–10:00, one day | Received |
| AVL runtime report, **22 Jul 2026** | 75,780 stop-level records; scheduled vs actual arrival/departure; 38 routes; 826 stops; 2,999 trips | Received (`data/Runtime_2026-07-22.xlsx`) |
| GTFS (`pta_wojhati_raw` Hive DB) | Network-wide stops/routes/schedules | Pending — export via `dataiku_webapp/` |
| Parking-violation records | Fines near bus stops | Not available |

Study parameters confirmed by operations: average blockage effect
**30 seconds** per case; OTP window **−1 minute to +5 minutes**.

## 3. Method

1. **Stop matching.** Each surveyed location was matched to its AVL stop ids
   by name, then verified against the routes listed by the field observers.
   9 of 11 locations matched cleanly. Two caveats: at *Al Jafliya* only route
   F09 of the listed routes (21A, C26, 88, F09) serves the matched bus-station
   stops in the AVL data, and at *Al Khail Mall* the listed routes F15/F17
   (not F16) serve the adjacent "Al Khail Gate" stop cluster. The physical
   stop clusters were retained; the route lists in the field table appear to
   be approximate.
2. **Exposure.** Bus arrivals at the matched stops were counted for the AM
   peak (07:00–09:59, matching the survey window) and an assumed symmetric PM
   peak (17:00–19:59).
3. **Baseline OTP.** Departure deviation (actual − scheduled, seconds) per
   stop record, classified early (< −60 s) / on-time / late (> +300 s).
4. **Impact model.** Each blocked-layby case delays one arriving bus by *D*
   seconds. The probability that this flips an otherwise on-time trip to
   late is estimated empirically as the share of peak departures already
   within *D* seconds of the +300 s threshold ("flip probability").
5. **Annualisation.** AM cases × (1 + PM factor) × operating days, with the
   PM factor defaulting to relative PM/AM bus exposure (1,147 / 1,254 = 0.91).

All computations are reproducible: `python3 analysis/runtime_analysis.py`
(outputs in `analysis/output/`). The scenario model with adjustable levers is
in `analysis/parking_otp_impact_model.xlsx`.

## 4. Baseline network performance (22 Jul 2026, 38 routes)

| Scope | n | On-time | Late (>5 min) | Early (>1 min) |
|---|---|---|---|---|
| All stop events | 72,679 | **87.2 %** | 10.9 % | 1.9 % |
| Peak stop events (AM+PM) | 25,478 | **85.5 %** | 12.7 % | 1.8 % |
| Trips, measured at terminal | 2,999 | **79.1 %** | 14.6 % | 6.3 % |

Late running already concentrates in the peaks — precisely when laybys are
blocked.

## 5. The 11 surveyed locations

| Location | Cases (3 h AM) | Bus arrivals AM peak | Buses/AM hour | Cases per 100 AM buses | OTP at stop (day) |
|---|---|---|---|---|---|
| Naif Intersection | 5 | 195 | 65 | 2.6 | 82.7 % |
| Burj Nahar | 5 | 195 | 65 | 2.6 | 84.5 % |
| Al Jafliya | 6 | 45 | 15 | 13.3 | 93.6 % |
| Emirates Tower | 3 | 48 | 16 | 6.2 | 91.6 % |
| Al Khail Mall | 2 | 211 | 70 | 0.9 | 93.3 % |
| Al Hana Center | 5 | 128 | 43 | 3.9 | 91.9 % |
| Burjuman | 7 | 77 | 26 | 9.1 | 90.2 % |
| Sharaf DG Metro | 8 | 179 | 60 | 4.5 | **78.7 %** |
| Al Rigga Metro | 5 | 31 | 10 | 16.1 | 83.5 % |
| Salah Al Din Metro | 4 | 43 | 14 | 9.3 | 91.5 % |
| Business Bay (all stops) | 10 | 102 | 34 | 9.8 | 93.9 % |
| **Total** | **60** | **1,254** | **418/h** | **4.8 avg** | — |

Notable: the worst OTP of the eleven (Sharaf DG Metro, 78.7 % vs 87.2 %
network) coincides with the highest blockage count (8 cases). PM-peak
exposure at the same stops is 1,147 arrivals — 91 % of AM.

## 6. Annual extrapolation (11 locations only)

`Annual cases = 60 AM cases × (1 + PM factor) × operating days`

| Scenario | PM factor | Days | Annual blocked-layby cases |
|---|---|---|---|
| Low | 0.80 | 250 | 27,000 |
| **Central** | **0.91** | **261 (working days)** | **≈ 30,000** |
| High | 1.00 | 305 | 36,600 |

At 30 s per case the central scenario represents **≈ 250 bus-hours of direct
delay per year**; at 60 s, ≈ 500 bus-hours. Weekends, midday and evening
occurrences are excluded (no observations), making these figures
conservative.

## 7. OTP impact

Flip probabilities measured from the peak deviation distribution at the 11
locations (2,286 peak stop events; 1,042 affected peak trips):

| Delay per case | P(stop event flips late) | P(trip flips late at terminal) | Extra late trips/yr (central) | ΔOTP, affected peak trips | ΔOTP, all 38 routes |
|---|---|---|---|---|---|
| 15 s | 1.3 % | 1.4 % | ≈ 430 | −0.16 pp | −0.04 pp |
| **30 s** | 2.1 % | 2.6 % | **≈ 780** | **−0.29 pp** | −0.07 pp |
| 60 s | 5.6 % | 6.3 % | ≈ 1,900 | −0.70 pp | −0.17 pp |
| 90 s | 8.8 % | 9.0 % | ≈ 2,700 | −1.00 pp | −0.25 pp |

Reading: with the operations estimate of 30 s per obstruction, illegal
parking at just these 11 locations pushes ~780 additional trips per year past
the +5-minute threshold — a 0.29-percentage-point OTP loss on the peak trips
that serve these stops. If queuing and re-approach push the true effect
toward 60–90 s (international observations, Section 9), the loss approaches
a full percentage point on affected trips.

Two structural notes:
- The +5-minute window absorbs small delays for trips running near schedule;
  the damage concentrates on trips **already 4–5 minutes behind** — i.e. the
  peak, where 12.7 % of events are already late.
- Repeated obstruction along one trip compounds: a trip passing Naif,
  Burj Nahar and Salah Al Din (routes 10/13A corridor) can be hit 2–3 times.
  The model counts each case once, again conservative.

## 8. Scaling beyond the 11 locations (network-wide, GTFS-based)

Every bus stop in the GTFS network (2,873 stops; 21,744 weekday bus trips)
was scored on the profile of the 11 surveyed sites: **AM-peak throughput at
least that of the survey cluster's lower quartile (≥ 46 arrivals/3 h) AND
metro/tram station within 200 m or mall/souq frontage** (computation:
`analysis/network_scoring.py`).

**112 stops fit the surveyed profile** (88 metro-adjacent, 23 mall-frontage) —
they form the **High-sensitivity tier**. The largest non-surveyed exposures
are Ibn Battuta Bus Station, Union Metro, Mall of the Emirates, Equiti Metro,
Gold Souq, Abu Baker Al Siddique Metro and Dubai Mall Metro. The remaining
stops are ranked by AM-peak throughput: the next 400 form the **Medium tier**
and the following 400 the **Low tier**; the residual ~1,600 stops (median
4 buses/hour) are treated as negligible. Full per-stop tiers:
`analysis/output/affected_stops.csv` and `network_stop_scores.csv`.

Case rates: High tier uses the survey-calibrated rate (60 cases / 2,084 GTFS
AM arrivals = **2.9 cases per 100 peak arrivals**); Medium and Low apply
**50 % and 25 % of that rate** — stated assumptions to be validated by spot
surveys, adjustable in the Excel model.

| Tier | Stops | AM-peak arrivals (share of network) | Annual cases | Delay @30 s | Extra late trips/yr @30 s / @60 s | ΔOTP on peak trips @30 s / @60 s |
|---|---|---|---|---|---|---|
| **High** (profile-matched) | 112 | 12,622 (24 %) | ≈ 182,000 | ≈ 1,510 bus-h | 4,700 / 11,500 | −0.18 / −0.45 pp |
| **Medium** (next 400 by throughput, 50 % rate) | 400 | 18,657 (36 %) | ≈ 134,000 | ≈ 1,120 bus-h | 3,480 / 8,500 | −0.14 / −0.33 pp |
| **Low** (following 400, 25 % rate) | 400 | 8,273 (16 %) | ≈ 30,000 | ≈ 250 bus-h | 770 / 1,880 | −0.03 / −0.07 pp |
| **Total** | **912** | **39,552 (76 %)** | **≈ 346,000** | **≈ 2,880 bus-h** | **8,950 / 21,880** | **−0.35 / −0.85 pp** |

(Peak-trip denominator: 9,771 weekday bus trips with a peak-hour stop event
× 261 days. Flip probabilities transferred from the 22 Jul AVL distribution.)

Caveats: several high-volume matches are bus-station laybys (Ibn Battuta,
Rashidiya, Gold Souq) where enforcement conditions differ from curbside
stops; the Medium/Low rate multipliers are assumptions, not measurements;
and the case rate is calibrated from a single day. A 1–2 week survey at
~10 High-tier and ~10 Medium-tier stops would firm all three tiers.

## 9. Benchmarking

| City | Programme | Penalty (approx.) | Reported outcomes |
|---|---|---|---|
| New York | MTA ACE — bus-mounted automated cameras ticket vehicles in bus stops/lanes | US$50 first offence, escalating to US$250 | Publicly reported: ~5 % faster buses on enforced routes, ~20 % fewer collisions, ~30 % drop in repeat violations |
| London | TfL bus stop clearways, CCTV-enforced 24/7 | PCN £160 (50 % early-payment discount) | Near-universal kerb access at stops; clearway compliance is a precondition of TfL's iBus OTP regime |
| Singapore | LTA camera-equipped buses enforce bus lanes/stops | ~S$150 composition fine | Sustained bus-lane compliance since bus-mounted cameras (2008) |
| Sydney | TfNSW bus-zone offence | ~A$390 | High deterrence via penalty level |
| **Dubai (today)** | Manual patrols; federal fine for stopping in a bus stop | **AED 500** | 60 cases / 3 h at 11 stops indicates low deterrence at current enforcement intensity |

Dubai's fine level is mid-range internationally; the gap is **automated,
continuous enforcement**. NYC's model (cameras on the buses themselves) is
the closest fit for high-frequency corridors like routes 10/13A/C01.

## 10. Detection & revenue potential

Cameras watch a layby continuously, so they detect more than the bus-
coinciding blockages counted in Section 8: off-peak events add **20 % of the
peak count** (PTA operations estimate). Not every detected event becomes
cash: an **enforceability rate of 70 %** (plate readable, genuinely stationary
in the marked layby, de-duplicated) and a **collection rate of 80 %** are
applied — a combined ticket-to-cash rate of **56 %**. The fine is **AED 200**
per violation (PTA direction; below the AED 500 federal bus-stop fine and
international peers, see Section 9).

A deterrence decay is built in deliberately: violations decline **25 %/year**
under continuous fixed enforcement (15 %/year under monthly-rotation portable
coverage), in line with NYC ACE experience. Revenue therefore **falls** every
year while the OTP and safety benefit **grows** — the fines fund the system
in years 1–3; the permanent return is service quality.

Year-1 detectable violations: ≈ 415,000 network-wide (346k peak cases
× 1.2), of which ≈ 290,000 become tickets and ≈ 232,000 are collected —
**≈ AED 46 M gross in year 1**, declining to ≈ AED 15 M by year 5.

## 11. ROI — two enforcement investment options

Camera costs are benchmark assumptions (no vendor quotes yet): fixed ANPR
site AED 40k capex + AED 5k/yr opex; portable unit AED 15k capex +
AED 60k/yr operational overhead (crew share, vehicle, redeployment,
maintenance). Horizon **5 years**, discount rate **7 %**. Computation:
`analysis/roi_model.py`; year-by-year tables in `analysis/output/roi_*.csv`.

### Option A — fixed cameras at all tiered stops (912)

| Tier | Capex | Opex/yr | Revenue yr 1 | 5-yr NPV (cash) | Payback |
|---|---|---|---|---|---|
| High (112 stops) | AED 4.5 M | 0.6 M | **24.4 M** | **+56.6 M** | < 1 year |
| Medium (400 stops) | 16.0 M | 2.0 M | 18.0 M | **+22.6 M** | ~1 year |
| Low (400 stops) | 16.0 M | 2.0 M | 4.0 M | **−13.8 M** | never |
| All 912 | 36.5 M | 4.6 M | 46.5 M | +65.4 M | ~1 year |

The Low tier destroys value under fixed cameras — violation density is too
thin to cover the fixed cost. **Option A should stop at High + Medium
(512 stops: capex 20.5 M, 5-yr NPV +79.2 M).**

### Option B — portable cameras, monthly rotation across High-tier stops

| Fleet | Capex | Opex/yr | Revenue yr 1 | 5-yr NPV (cash) | Payback |
|---|---|---|---|---|---|
| 20 units | AED 0.3 M | 1.2 M | 4.4 M | **+8.3 M** | < 1 year |
| 30 units | 0.45 M | 1.8 M | 6.5 M | **+12.5 M** | < 1 year |
| 40 units | 0.6 M | 2.4 M | 8.7 M | **+16.6 M** | < 1 year |
| 50 units | 0.75 M | 3.0 M | 10.9 M | **+20.8 M** | < 1 year |

Portable economics rest on targeting: at High-tier stops each deployed
camera sees ≈ 7.5 events/day (≈ AED 830/day in collected fines vs ≈ AED
240/day all-in cost). The same unit at a Low-tier stop would roughly break
even — portable value comes from following the violation density, plus a
"cameras could be anywhere" deterrence halo that fixed sites lack.

### Recommended: hybrid

1. **Fixed cameras at High + Medium tiers** (512 stops) — NPV +79 M,
   self-funding within year 1.
2. **A 20–30 unit portable fleet** rotating across Low-tier and emerging
   hotspots — NPV +8–13 M, and it doubles as the measurement tool that
   validates the tier assumptions (Section 8).
3. Revenue is a declining curve by design; the business case should be sold
   on OTP recovery (up to +0.85 pp peak) and elimination of live-lane
   boarding, with fines as the financing bridge.

Sensitivity worth noting: at the federal AED 500 fine level, all figures
scale ×2.5 — even the Low tier turns positive. **Who retains the fine
revenue (RTA vs the wider government fine system) is unconfirmed and is the
single biggest swing factor in the cash ROI.**

## 12. Recommendations

1. **Pilot automated enforcement** (bus-mounted or pole-mounted cameras) at
   the five worst sites: Sharaf DG Metro, Business Bay, Burjuman, Naif
   Intersection, Burj Nahar. Measure OTP before/after — this study provides
   the baseline.
2. **Design fixes** where violators are dropping off passengers (taxi/limo
   dominant): marked drop-off bays 30–50 m from the layby at metro stops.
3. **Extend the survey**: multi-day AM+PM observation, and log blockage
   *duration* per case to replace the single 30 s assumption.
4. **Data pipeline**: monthly join of AVL runtime × violation records (once
   available) to track the KPI "obstructed arrivals per 100 peak buses".

## 13. Limitations

- One-day, AM-only field sample; PM assumed at 91 % of AM intensity.
- Single-value 30 s delay assumption; international evidence suggests
  obstruction cost is often higher (hence the 60/90 s scenarios).
- Flip probabilities derive from one day of AVL data (22 Jul 2026).
- OTP computed at stop level from AVL departures; RTA's official OTP
  measurement points may differ, which shifts levels but not the mechanism.
- Route lists at 2 of 11 locations did not fully match AVL service; the
  physical stop clusters were used.
- No violation records were available to validate observation counts.

---

*Reproduce: `python3 analysis/runtime_analysis.py` · Scenario model:
`analysis/parking_otp_impact_model.xlsx` · Base data & parameters:
`STUDY_NOTES.md`*
