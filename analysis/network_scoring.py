#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network-wide affected-stop identification (STUDY.md section 8).

Scores every bus stop in the GTFS network on the risk profile of the 11
field-surveyed locations (high peak throughput + metro/mall adjacency) to
estimate how many stops share the illegal-parking exposure, and scales the
annual case count accordingly.

Inputs : gtfs/stops.txt, gtfs/stop_times.txt.gz, gtfs/trips.txt,
         gtfs/routes.txt, gtfs/calendar.txt
Outputs: analysis/output/network_stop_scores.csv   (every bus stop, scored)
         analysis/output/affected_stops.csv        (stops matching profile)
         analysis/output/network_scaling.csv       (scaled annual estimates)

Usage:  python3 analysis/network_scoring.py
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "..", "gtfs")
OUT = os.path.join(HERE, "output")

AM_HOURS = (7, 8, 9)          # 07:00-09:59
PM_HOURS = (17, 18, 19)       # 17:00-19:59
METRO_RADIUS_M = 200          # bus stop within this distance of a metro/tram
                              # station counts as station-adjacent
MALL_WORDS = ("mall", "center", "centre", "souk", "souq", "plaza",
              "shopping", "city centre", "burjuman", "market")

# survey-derived calibration (see STUDY.md sections 5-7)
SURVEY_CASES_AM = 60.0   # observed cases, 11 locations, one AM peak
N_MEDIUM = 400           # next-N stops by AM-peak throughput -> Medium tier
N_LOW = 400              # following N stops -> Low tier
TIER_RATE_MULT = {"High": 1.0, "Medium": 0.5, "Low": 0.25}  # of survey rate
PM_FACTOR = 1147.0 / 1254.0
OPERATING_DAYS = 261
P_FLIP_30S = 0.0259
P_FLIP_60S = 0.0633

# the 27 AVL stop ids of the 11 surveyed locations (GTFS uses same ids)
SURVEY_STOP_IDS = {
    "112001", "112002", "114001", "114002", "256102", "256103", "256106",
    "136101", "895501", "540101", "165101", "166101", "466101", "455001",
    "455002", "400001", "400002", "202101", "202102", "203201", "155001",
    "155002", "140001", "140002", "314102", "314103", "611102",
}


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def main():
    os.makedirs(OUT, exist_ok=True)
    stops = pd.read_csv(os.path.join(G, "stops.txt"), dtype=str)
    stops["stop_lat"] = stops["stop_lat"].astype(float)
    stops["stop_lon"] = stops["stop_lon"].astype(float)
    routes = pd.read_csv(os.path.join(G, "routes.txt"), dtype=str)
    trips = pd.read_csv(os.path.join(G, "trips.txt"), dtype=str)
    cal = pd.read_csv(os.path.join(G, "calendar.txt"), dtype=str)
    st = pd.read_csv(os.path.join(G, "stop_times.txt.gz"), dtype=str,
                     usecols=["trip_id", "arrival_time", "stop_id"])

    # ---- representative weekday: Tuesday services -----------------------
    weekday_services = set(cal.loc[cal["tuesday"] == "1", "service_id"])
    bus_routes = set(routes.loc[routes["route_type"] == "3", "route_id"])
    rail_routes = set(routes.loc[routes["route_type"] != "3", "route_id"])

    trips_idx = trips.set_index("trip_id")
    day_trips = trips[trips["service_id"].isin(weekday_services)]
    day_bus_trips = set(day_trips.loc[day_trips["route_id"].isin(bus_routes),
                                      "trip_id"])
    rail_trips = set(trips.loc[trips["route_id"].isin(rail_routes), "trip_id"])
    print(f"weekday(Tue) bus trips: {len(day_bus_trips):,} "
          f"of {len(trips):,} total trips")

    # ---- metro/tram station locations -----------------------------------
    rail_stop_ids = set(st.loc[st["trip_id"].isin(rail_trips), "stop_id"])
    rail_stops = stops[stops["stop_id"].isin(rail_stop_ids)]
    print(f"rail (metro/tram) station stops: {len(rail_stops)}")

    # ---- peak arrivals per stop (weekday bus service) --------------------
    stb = st[st["trip_id"].isin(day_bus_trips)].copy()
    hrs = stb["arrival_time"].str.slice(0, 2).astype(int) % 24
    stb["am"] = hrs.isin(AM_HOURS)
    stb["pm"] = hrs.isin(PM_HOURS)
    per_stop = stb.groupby("stop_id").agg(
        buses_day=("trip_id", "count"),
        buses_am_peak=("am", "sum"),
        buses_pm_peak=("pm", "sum")).reset_index()
    per_stop["routes_served"] = stb.merge(
        trips_idx[["route_id"]], left_on="trip_id", right_index=True) \
        .groupby("stop_id")["route_id"].nunique().reindex(
            per_stop["stop_id"]).values

    df = stops.merge(per_stop, on="stop_id", how="inner")
    df = df[df["buses_day"] > 0]

    # ---- context flags ----------------------------------------------------
    rl = rail_stops[["stop_lat", "stop_lon"]].values
    if len(rl):
        d = np.array([haversine_m(row.stop_lat, row.stop_lon,
                                  rl[:, 0], rl[:, 1]).min()
                      for row in df.itertuples()])
    else:
        d = np.full(len(df), np.inf)
    df["metro_dist_m"] = d.round(0)
    df["near_metro"] = df["metro_dist_m"] <= METRO_RADIUS_M
    name_lc = df["stop_name"].fillna("").str.lower()
    df["mall_frontage"] = name_lc.str.contains("|".join(MALL_WORDS))
    df["is_surveyed"] = df["stop_id"].isin(SURVEY_STOP_IDS)

    # ---- risk profile from the surveyed stops ----------------------------
    surveyed = df[df["is_surveyed"]]
    thr_am = surveyed["buses_am_peak"].quantile(0.25)  # lower quartile
    print(f"\nsurveyed stops found in GTFS: {len(surveyed)}/27")
    print(f"AM-peak arrivals at surveyed stops: "
          f"min={surveyed['buses_am_peak'].min():.0f}, "
          f"q25={thr_am:.0f}, median={surveyed['buses_am_peak'].median():.0f}")

    # affected = comparable throughput AND (metro-adjacent OR mall frontage)
    df["affected"] = (df["buses_am_peak"] >= thr_am) & \
                     (df["near_metro"] | df["mall_frontage"])
    df.loc[df["is_surveyed"], "affected"] = True

    aff = df[df["affected"]].sort_values("buses_am_peak", ascending=False)
    n_aff = len(aff)
    exp_am = aff["buses_am_peak"].sum()
    print(f"\naffected stops (incl. 27 surveyed): {n_aff}")
    print(f"  of which near metro: {aff['near_metro'].sum()}, "
          f"mall frontage: {aff['mall_frontage'].sum()}")
    print(f"AM-peak bus arrivals at affected stops: {exp_am:,.0f} "
          f"(surveyed 27: {surveyed['buses_am_peak'].sum():,.0f})")

    # ---- three-tier risk model -------------------------------------------
    # High   = the profile-matched stops (survey-calibrated case rate)
    # Medium = next N_MEDIUM stops by AM-peak throughput (assumed 50% rate)
    # Low    = following N_LOW stops (assumed 25% rate)
    # Case rate calibrated on the SAME exposure basis used for scaling:
    # GTFS AM-peak arrivals (all routes) at the 27 surveyed stops.
    survey_exp_am = surveyed["buses_am_peak"].sum()
    rate = SURVEY_CASES_AM / survey_exp_am  # cases per AM-peak bus arrival
    print(f"\ncalibrated case rate: {100 * rate:.2f} cases per 100 AM-peak "
          f"arrivals (GTFS basis)")

    df["tier"] = "Minimal"
    df.loc[df["affected"], "tier"] = "High"
    rest = df[~df["affected"]].sort_values("buses_am_peak", ascending=False)
    df.loc[rest.index[:N_MEDIUM], "tier"] = "Medium"
    df.loc[rest.index[N_MEDIUM:N_MEDIUM + N_LOW], "tier"] = "Low"

    # denominators for dOTP: weekday bus trips with a peak-hour stop event
    n_day_trips = len(day_bus_trips)
    peak_trip_ids = set(stb.loc[stb["am"] | stb["pm"], "trip_id"])
    n_peak_trips = len(peak_trip_ids)
    annual_peak_trips = n_peak_trips * OPERATING_DAYS
    print(f"weekday bus trips: {n_day_trips:,} | with a peak-hour stop "
          f"event: {n_peak_trips:,}")

    tiers = []
    for tier, mult in TIER_RATE_MULT.items():
        sub = df[df["tier"] == tier]
        arr = sub["buses_am_peak"].sum()
        cases_am = arr * rate * mult
        annual = cases_am * (1 + PM_FACTOR) * OPERATING_DAYS
        tiers.append(dict(
            tier=tier, stops=len(sub),
            am_peak_arrivals=int(arr),
            pct_network_exposure=round(100 * arr
                                       / df["buses_am_peak"].sum(), 1),
            rate_multiplier=mult,
            cases_per_am_peak=round(cases_am, 0),
            annual_cases=round(annual, -2),
            annual_delay_h_30s=round(annual * 30 / 3600.0, 0),
            extra_late_trips_30s=round(annual * P_FLIP_30S, -1),
            extra_late_trips_60s=round(annual * P_FLIP_60S, -1),
            dOTP_peak_pp_30s=round(100 * annual * P_FLIP_30S
                                   / annual_peak_trips, 2),
            dOTP_peak_pp_60s=round(100 * annual * P_FLIP_60S
                                   / annual_peak_trips, 2),
        ))
    tier_df = pd.DataFrame(tiers)
    total = tier_df.drop(columns=["tier", "rate_multiplier"]).sum()
    total["tier"], total["rate_multiplier"] = "TOTAL", ""
    total["pct_network_exposure"] = round(
        100 * tier_df["am_peak_arrivals"].sum() / df["buses_am_peak"].sum(), 1)
    tier_df = pd.concat([tier_df, total.to_frame().T], ignore_index=True)
    print("\n", tier_df.to_string(index=False))
    print("\ntop 15 affected stops by AM-peak arrivals (non-surveyed):")
    top = aff[~aff["is_surveyed"]].head(15)
    print(top[["stop_id", "stop_name", "buses_am_peak", "routes_served",
               "metro_dist_m", "mall_frontage"]].to_string(index=False))

    keep = ["stop_id", "stop_name", "buses_day", "buses_am_peak",
            "buses_pm_peak", "routes_served", "metro_dist_m", "near_metro",
            "mall_frontage", "is_surveyed", "affected", "tier"]
    df[keep].sort_values("buses_am_peak", ascending=False).to_csv(
        os.path.join(OUT, "network_stop_scores.csv"), index=False)
    df.loc[df["tier"] != "Minimal", keep].sort_values(
        ["tier", "buses_am_peak"], ascending=[True, False]).to_csv(
        os.path.join(OUT, "affected_stops.csv"), index=False)
    tier_df.to_csv(os.path.join(OUT, "tier_summary.csv"), index=False)
    print("\noutputs written to", OUT)


if __name__ == "__main__":
    main()
