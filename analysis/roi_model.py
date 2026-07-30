#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enforcement ROI model - illegal parking at bus stops (STUDY.md sections 10-11).

Option A: fixed ANPR cameras at all tiered stops (per-tier economics).
Option B: portable cameras rotating monthly across High-tier stops,
          fleet variants of 20/30/40/50 units.

All monetary values in AED. Camera costs are benchmark assumptions (no RTA
quotes available); fine level, horizon, discount rate and off-peak factor
per PTA direction (Jul 2026).

Outputs: analysis/output/roi_option_a.csv       (per tier x year cash flows)
         analysis/output/roi_option_b.csv       (per fleet size x year)
         analysis/output/roi_summary.csv        (NPV/payback comparison)

Usage:  python3 analysis/roi_model.py
"""

import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")

# ---- confirmed parameters (user, Jul 2026) --------------------------------
FINE_AED = 200.0
YEARS = 5
DISCOUNT = 0.07
OFFPEAK_FACTOR = 0.20        # off-peak events = 20% of peak events
PORTABLE_FLEETS = [20, 30, 40, 50]

# ---- tier baselines (analysis/network_scoring.py, tier_summary.csv) -------
TIERS = {
    #        stops, annual peak cases (year-0 baseline)
    "High":   (112, 181_600.0),
    "Medium": (400, 134_200.0),
    "Low":    (400,  29_800.0),
}
OPERATING_DAYS = 261
DELAY_H_30S_TOTAL = 2_879.0          # bus-hours/yr, all tiers, 30 s per case
TOTAL_CASES = sum(v[1] for v in TIERS.values())

# ---- benchmark assumptions (labelled, adjustable) --------------------------
ENFORCEABILITY = 0.70    # detected events producing a valid ticket
COLLECTION = 0.80        # tickets paid
DECAY_FIXED = 0.25       # annual violation decline under 24/7 fixed cameras
DECAY_PORTABLE = 0.15    # annual decline under monthly-rotation coverage
CAPEX_FIXED_SITE = 40_000.0    # ANPR camera, pole, power, comms, install
OPEX_FIXED_SITE = 5_000.0      # per site per year
CAPEX_PORTABLE_UNIT = 15_000.0
OPEX_PORTABLE_UNIT = 60_000.0  # crew share, vehicle, redeploy, maintenance
BUS_COST_PER_H = 250.0         # bus operating cost, delay-savings valuation

TICKET_RATE = ENFORCEABILITY * COLLECTION   # 0.56


def pv(amount, year):
    return amount / (1 + DISCOUNT) ** year


def option_a():
    rows, summary = [], []
    for tier, (stops, peak_cases) in TIERS.items():
        detectable0 = peak_cases * (1 + OFFPEAK_FACTOR)   # cameras see 24/7
        capex = stops * CAPEX_FIXED_SITE
        opex = stops * OPEX_FIXED_SITE
        delay_h0 = DELAY_H_30S_TOTAL * peak_cases / TOTAL_CASES
        pv_rev = pv_opex = pv_delay = 0.0
        cum_cash, payback = -capex, None
        for t in range(1, YEARS + 1):
            viol = detectable0 * (1 - DECAY_FIXED) ** (t - 1)
            revenue = viol * TICKET_RATE * FINE_AED
            # delay avoided vs no-enforcement baseline (peak cases decline
            # at the same rate as detectable violations)
            delay_saved = delay_h0 * (1 - (1 - DECAY_FIXED) ** (t - 1)) \
                * BUS_COST_PER_H
            pv_rev += pv(revenue, t)
            pv_opex += pv(opex, t)
            pv_delay += pv(delay_saved, t)
            cum_cash += revenue - opex
            if payback is None and cum_cash >= 0:
                payback = t
            rows.append(dict(tier=tier, year=t, tickets=round(
                viol * ENFORCEABILITY), revenue_m=round(revenue / 1e6, 2),
                opex_m=round(opex / 1e6, 2),
                delay_saved_m=round(delay_saved / 1e6, 2)))
        npv_cash = pv_rev - pv_opex - capex
        summary.append(dict(
            option="A fixed", scope=f"{tier} ({stops} stops)",
            capex_m=round(capex / 1e6, 2),
            opex_m_per_yr=round(opex / 1e6, 2),
            rev_y1_m=round(detectable0 * TICKET_RATE * FINE_AED / 1e6, 2),
            npv_cash_m=round(npv_cash / 1e6, 1),
            npv_econ_m=round((npv_cash + pv_delay) / 1e6, 1),
            payback_yr=payback if payback else ">5"))
    return pd.DataFrame(rows), summary


def option_b():
    # portable units target High-tier stops, rotating monthly
    stops_h, peak_cases_h = TIERS["High"]
    det_per_stop_day0 = peak_cases_h * (1 + OFFPEAK_FACTOR) \
        / OPERATING_DAYS / stops_h            # ~ 7.5 events/stop/day
    rows, summary = [], []
    for n in PORTABLE_FLEETS:
        capex = n * CAPEX_PORTABLE_UNIT
        opex = n * OPEX_PORTABLE_UNIT
        pv_rev = pv_opex = 0.0
        cum_cash, payback = -capex, None
        for t in range(1, YEARS + 1):
            per_stop_day = det_per_stop_day0 * (1 - DECAY_PORTABLE) ** (t - 1)
            revenue = n * per_stop_day * OPERATING_DAYS * TICKET_RATE \
                * FINE_AED
            pv_rev += pv(revenue, t)
            pv_opex += pv(opex, t)
            cum_cash += revenue - opex
            if payback is None and cum_cash >= 0:
                payback = t
            rows.append(dict(fleet=n, year=t,
                             tickets=round(n * per_stop_day * OPERATING_DAYS
                                           * ENFORCEABILITY),
                             revenue_m=round(revenue / 1e6, 2),
                             opex_m=round(opex / 1e6, 2)))
        npv = pv_rev - pv_opex - capex
        summary.append(dict(
            option="B portable", scope=f"{n} units (High tier rotation)",
            capex_m=round(capex / 1e6, 2),
            opex_m_per_yr=round(opex / 1e6, 2),
            rev_y1_m=round(n * det_per_stop_day0 * OPERATING_DAYS
                           * TICKET_RATE * FINE_AED / 1e6, 2),
            npv_cash_m=round(npv / 1e6, 1),
            npv_econ_m="",   # delay savings negligible at <=5% coverage
            payback_yr=payback if payback else ">5"))
    return pd.DataFrame(rows), summary


def main():
    os.makedirs(OUT, exist_ok=True)
    a_rows, a_sum = option_a()
    b_rows, b_sum = option_b()
    a_rows.to_csv(os.path.join(OUT, "roi_option_a.csv"), index=False)
    b_rows.to_csv(os.path.join(OUT, "roi_option_b.csv"), index=False)
    s = pd.DataFrame(a_sum + b_sum)
    s.to_csv(os.path.join(OUT, "roi_summary.csv"), index=False)
    print("Assumptions: fine AED %.0f, ticket rate %.0f%%, decay fixed %.0f%%"
          "/yr portable %.0f%%/yr, %d yrs @ %.0f%%"
          % (FINE_AED, 100 * TICKET_RATE, 100 * DECAY_FIXED,
             100 * DECAY_PORTABLE, YEARS, 100 * DISCOUNT))
    print("\n", s.to_string(index=False))
    print("\nOption A year-by-year:\n", a_rows.to_string(index=False))
    print("\nOption B year-by-year:\n",
          b_rows[b_rows["fleet"].isin([20, 50])].to_string(index=False))


if __name__ == "__main__":
    main()
