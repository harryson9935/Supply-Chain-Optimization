"""
scenario_analysis.py
---------------------
Runs the optimization model under multiple real-world scenarios to
support data-driven, robust supply-chain decisions:

    1. Baseline               - current-state costs/tariffs/risk
    2. High Tariff (Trade War) - tariffs doubled on all lanes
    3. Supplier Disruption     - top China suppliers (S4, S5) knocked out
    4. Demand Surge            - +30% demand (e.g., post-pandemic capacity build-out)
    5. Facility Outage         - largest facility (F3, Chennai) offline
    6. Risk-Averse Sourcing    - risk premium weighted 3x higher

Outputs a comparison table + per-scenario flow/cost detail into /results.
"""

import os
import pandas as pd
from model import build_and_solve

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS, exist_ok=True)

SCENARIOS = {
    "Baseline": {},
    "High Tariff (Trade War)": {"tariff_multiplier": 2.0},
    "Supplier Disruption (China)": {"disable_suppliers": ["S4", "S5"]},
    "Demand Surge (+30%)": {"demand_multiplier": 1.3},
    "Facility Outage (Chennai)": {"disable_facilities": ["F3"]},
    "Risk-Averse Sourcing (3x premium)": {"risk_premium_per_unit": 1200},
}


def run_all():
    summary_rows = []
    for name, overrides in SCENARIOS.items():
        print(f"Solving scenario: {name} ...")
        result = build_and_solve(scenario_overrides=overrides, verbose=False)
        row = {
            "scenario": name,
            "status": result["status"],
            "total_cost": result["total_cost"],
            **{f"cost__{k}": v for k, v in result["cost_breakdown"].items() if k != "total_cost"},
            "facilities_open": ", ".join(result["facilities_open"]),
            "num_facilities_open": len(result["facilities_open"]),
        }
        summary_rows.append(row)

        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("+", "").replace("%", "pct").replace(",","")
        result["flows_supplier_facility"].to_csv(os.path.join(RESULTS, f"flows_sf__{safe_name}.csv"), index=False)
        result["flows_facility_demand"].to_csv(os.path.join(RESULTS, f"flows_fd__{safe_name}.csv"), index=False)

    summary = pd.DataFrame(summary_rows)
    summary["cost_delta_vs_baseline"] = summary["total_cost"] - summary.loc[summary.scenario == "Baseline", "total_cost"].values[0]
    summary["pct_change_vs_baseline"] = (summary["cost_delta_vs_baseline"] / summary.loc[summary.scenario == "Baseline", "total_cost"].values[0] * 100).round(2)
    summary.to_csv(os.path.join(RESULTS, "scenario_comparison.csv"), index=False)
    print("\n=== Scenario Comparison ===")
    print(summary[["scenario", "status", "total_cost", "pct_change_vs_baseline", "num_facilities_open"]].to_string(index=False))
    return summary


if __name__ == "__main__":
    run_all()
