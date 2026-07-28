#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illegal parking at bus stops - baseline analysis from AVL runtime data.

Input : data/Runtime_2026-07-22.xlsx  (stop-level AVL records, 22 Jul 2026,
        38 routes serving the 11 field-surveyed locations)
Output: analysis/output/*.csv  (all tables used in STUDY.md)

OTP rule (RTA): a departure is ON TIME if it is no more than 1 minute early
and no more than 5 minutes late:  -60 s <= deviation <= +300 s.

Usage:  python3 analysis/runtime_analysis.py
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(HERE, "..", "data", "Runtime_2026-07-22.xlsx")
OUT = os.path.join(HERE, "output")

EARLY_S = -60      # more than 1 min early -> "early"
LATE_S = 300       # more than 5 min late  -> "late"
AM_PEAK = [7, 8, 9]        # 07:00-09:59 (survey window)
PM_PEAK = [17, 18, 19]     # 17:00-19:59 (assumed evening peak)
DELAY_SCENARIOS = [15, 30, 60, 90]   # seconds added per obstructed arrival

# 11 field-surveyed locations -> AVL stop ids (matched by name + route
# cross-check; see STUDY.md section "Stop matching" for the two caveats).
LOCATIONS = {
    "Naif Intersection":  [112001, 112002],
    "Burj Nahar":         [114001, 114002],
    "Al Jafliya":         [256102, 256103, 256106],
    "Emirates Tower":     [136101, 895501],
    "Al Khail Mall":      [540101, 165101, 166101, 466101],
    "Al Hana Center":     [455001, 455002],
    "Burjuman":           [400001, 400002],
    "Sharaf DG Metro":    [202101, 202102, 203201],
    "Al Rigga Metro":     [155001, 155002],
    "Salah Al Din Metro": [140001, 140002],
    "Business Bay":       [314102, 314103, 611102],
}

# blocked-layby cases observed 07:00-10:00 on the survey day (one day)
CASES_AM = {
    "Naif Intersection": 5, "Burj Nahar": 5, "Al Jafliya": 6,
    "Emirates Tower": 3, "Al Khail Mall": 2, "Al Hana Center": 5,
    "Burjuman": 7, "Sharaf DG Metro": 8, "Al Rigga Metro": 5,
    "Salah Al Din Metro": 4, "Business Bay": 10,
}


def load():
    df = pd.read_excel(INPUT)
    df["Route"] = df["Route"].astype(str)
    df["dev"] = pd.to_numeric(df["Diff_in_seconds"], errors="coerce")
    df["OP_Hour"] = pd.to_numeric(df["OP_Hour"], errors="coerce")
    df["status"] = np.where(
        df["dev"] < EARLY_S, "early",
        np.where(df["dev"] > LATE_S, "late", "ontime"))
    df.loc[df["dev"].isna(), "status"] = "nodata"
    return df


def otp_share(frame):
    valid = frame[frame["dev"].notna()]
    if not len(valid):
        return np.nan
    return (valid["status"] == "ontime").mean()


def main():
    os.makedirs(OUT, exist_ok=True)
    df = load()
    valid = df[df["dev"].notna()]
    peak = valid[valid["OP_Hour"].isin(AM_PEAK + PM_PEAK)]

    # ---- network baseline (stop-event level and trip level) -------------
    last = valid.sort_values("Stop_Seq").groupby("Trip_ID").tail(1)
    baseline = pd.DataFrame([
        dict(scope="all stop events", n=len(valid),
             ontime=otp_share(valid),
             late=(valid["status"] == "late").mean(),
             early=(valid["status"] == "early").mean()),
        dict(scope="peak stop events", n=len(peak),
             ontime=otp_share(peak),
             late=(peak["status"] == "late").mean(),
             early=(peak["status"] == "early").mean()),
        dict(scope="trips (terminal stop)", n=len(last),
             ontime=otp_share(last),
             late=(last["status"] == "late").mean(),
             early=(last["status"] == "early").mean()),
    ]).round(4)
    baseline.to_csv(os.path.join(OUT, "network_baseline.csv"), index=False)

    # ---- per-route OTP ---------------------------------------------------
    route = valid.groupby("Route").apply(
        lambda g: pd.Series({
            "stop_events": len(g),
            "trips": g["Trip_ID"].nunique(),
            "otp": otp_share(g),
            "late": (g["status"] == "late").mean(),
            "early": (g["status"] == "early").mean(),
            "mean_dev_s": g["dev"].mean(),
        })).round(3).sort_values("otp")
    route.to_csv(os.path.join(OUT, "route_otp.csv"))

    # ---- the 11 locations --------------------------------------------------
    rows, sel_frames = [], []
    for loc, stops in LOCATIONS.items():
        sub = df[df["Stop_ID"].isin(stops)]
        am = sub[sub["OP_Hour"].isin(AM_PEAK)]
        pm = sub[sub["OP_Hour"].isin(PM_PEAK)]
        rows.append(dict(
            location=loc, n_stops=len(stops), cases_am=CASES_AM[loc],
            buses_day=len(sub), buses_am_peak=len(am), buses_pm_peak=len(pm),
            buses_per_am_hour=round(len(am) / 3.0, 1),
            cases_per_100_am_buses=round(100.0 * CASES_AM[loc] / len(am), 1)
            if len(am) else np.nan,
            otp_day=round(otp_share(sub), 3),
            otp_am_peak=round(otp_share(am), 3),
            late_share_day=round((sub[sub["dev"].notna()]["status"] == "late")
                                 .mean(), 3),
        ))
        sel_frames.append(sub)
    loc_df = pd.DataFrame(rows)
    loc_df.to_csv(os.path.join(OUT, "locations.csv"), index=False)

    # ---- flip-to-late probabilities -------------------------------------
    sel = pd.concat(sel_frames).drop_duplicates(
        subset=["Trip_ID", "Stop_ID", "Stop_Seq"])
    sel_peak = sel[sel["OP_Hour"].isin(AM_PEAK + PM_PEAK) & sel["dev"].notna()]
    term_aff = last[last["Trip_ID"].isin(sel_peak["Trip_ID"].unique())]
    flips = []
    for d in DELAY_SCENARIOS:
        flips.append(dict(
            delay_s=d,
            p_flip_stop_event=((sel_peak["dev"] > LATE_S - d)
                               & (sel_peak["dev"] <= LATE_S)).mean(),
            p_flip_trip_terminal=((term_aff["dev"] > LATE_S - d)
                                  & (term_aff["dev"] <= LATE_S)).mean(),
        ))
    flip_df = pd.DataFrame(flips).round(4)
    flip_df.to_csv(os.path.join(OUT, "flip_probabilities.csv"), index=False)

    # ---- console summary --------------------------------------------------
    print(baseline.to_string(index=False))
    print("\n11 locations:\n", loc_df.to_string(index=False))
    print("\nflip probabilities (peak, 11 locations):\n",
          flip_df.to_string(index=False))
    print("\npeak stop events at 11 locations:", len(sel_peak),
          "| affected peak trips:", len(term_aff))
    print("\nCSV outputs written to", OUT)


if __name__ == "__main__":
    main()
