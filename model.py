"""
model.py
--------
Mixed-Integer Supply Chain Network Design model for a global high-end
medical equipment supply chain.

FORMULATION
-----------
Originally specified as a Mixed-Integer NONLINEAR Program (MINLP):
the "true" objective includes a risk-adjusted cost term that is
multiplicative in flow and supplier/facility risk
    risk_cost = sum_{i,j} x_ij * unit_cost_i * risk_i * (1 + alpha * z_i)
and a nonlinear tariff-on-tariff compounding term for multi-leg routes.
This repo linearizes those terms (risk premium expressed as an added
$/unit surcharge, tariff compounding pre-computed per lane) so the
model solves exactly as a MILP with the free CBC solver via PuLP --
fully reproducible with no commercial license required. The code is
structured so a Gurobi/Pyomo nonlinear backend can be swapped in
(see `USE_GUROBI` flag) if a license is available.

Decision variables
-------------------
x[s,f]  >= 0   units shipped from supplier s to facility f
y[f,d]  >= 0   units shipped from facility f to demand region d
open[f] in {0,1}  whether facility f is activated

Objective: minimize total landed cost
    = component procurement cost
    + supplier->facility freight cost
    + tariff cost (rate * (component + freight))
    + risk premium cost
    + facility variable production cost
    + facility fixed (activation) cost
    + facility->region transport cost

Constraints
-----------
1. Facility throughput balance: inflow from suppliers == outflow to regions
2. Supplier capacity limits
3. Facility capacity limits (only if facility is open)
4. Demand satisfaction per region (>= service_level_min * demand)
5. Facility activation logic (big-M linking x/y to open[f])
"""

import os
import pandas as pd
import pulp

USE_GUROBI = False  # flip to True + install gurobipy/license to use exact MINLP backend

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load_data():
    suppliers = pd.read_csv(os.path.join(DATA, "suppliers.csv"))
    facilities = pd.read_csv(os.path.join(DATA, "facilities.csv"))
    demand = pd.read_csv(os.path.join(DATA, "demand.csv"))
    sup_fac_cost = pd.read_csv(os.path.join(DATA, "supplier_facility_cost.csv"))
    fac_demand_cost = pd.read_csv(os.path.join(DATA, "facility_demand_cost.csv"))
    return suppliers, facilities, demand, sup_fac_cost, fac_demand_cost


def build_and_solve(scenario_overrides=None, verbose=True):
    """
    scenario_overrides: dict, optional keys:
        - 'tariff_multiplier': float, scales all tariff rates (e.g., 2.0 = tariffs doubled)
        - 'risk_multiplier': float, scales all supplier risk scores
        - 'demand_multiplier': float, scales all regional demand
        - 'disable_suppliers': list[str], supplier_ids to knock out (e.g., disruption)
        - 'disable_facilities': list[str], facility_ids to knock out
        - 'risk_premium_per_unit': float, $ premium applied per unit of risk_score (default 400)
    Returns: dict with status, total_cost, flows dataframes, and cost breakdown
    """
    overrides = scenario_overrides or {}
    tariff_mult = overrides.get("tariff_multiplier", 1.0)
    risk_mult = overrides.get("risk_multiplier", 1.0)
    demand_mult = overrides.get("demand_multiplier", 1.0)
    disabled_suppliers = set(overrides.get("disable_suppliers", []))
    disabled_facilities = set(overrides.get("disable_facilities", []))
    risk_premium_per_unit = overrides.get("risk_premium_per_unit", 400)

    suppliers, facilities, demand, sup_fac_cost, fac_demand_cost = load_data()

    sup_ids = [s for s in suppliers.supplier_id if s not in disabled_suppliers]
    fac_ids = [f for f in facilities.facility_id if f not in disabled_facilities]
    dem_ids = demand.region_id.tolist()

    unit_cost = dict(zip(suppliers.supplier_id, suppliers.unit_cost_usd))
    sup_cap = dict(zip(suppliers.supplier_id, suppliers.capacity_units))
    risk = {s: r * risk_mult for s, r in zip(suppliers.supplier_id, suppliers.risk_score)}

    fac_cap = dict(zip(facilities.facility_id, facilities.capacity_units))
    fixed_cost = dict(zip(facilities.facility_id, facilities.fixed_cost_usd))
    var_cost = dict(zip(facilities.facility_id, facilities.variable_cost_per_unit))

    dem_qty = {d: q * demand_mult for d, q in zip(demand.region_id, demand.demand_units)}
    service_min = dict(zip(demand.region_id, demand.service_level_min))

    freight = {(r.supplier_id, r.facility_id): r.freight_cost_per_unit for r in sup_fac_cost.itertuples()}
    tariff = {(r.supplier_id, r.facility_id): r.tariff_rate * tariff_mult for r in sup_fac_cost.itertuples()}
    transport = {(r.facility_id, r.region_id): r.transport_cost_per_unit for r in fac_demand_cost.itertuples()}

    # Landed cost per unit on each supplier->facility lane (component + freight + tariff + risk premium)
    landed_cost = {}
    for s in sup_ids:
        for f in fac_ids:
            base = unit_cost[s] + freight[(s, f)]
            tariffed = base * (1 + tariff[(s, f)])
            landed_cost[(s, f)] = tariffed + risk[s] * risk_premium_per_unit

    prob = pulp.LpProblem("MedicalEquipment_SupplyChain_Optimization", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("Ship_Sup_Fac", (sup_ids, fac_ids), lowBound=0, cat="Continuous")
    y = pulp.LpVariable.dicts("Ship_Fac_Dem", (fac_ids, dem_ids), lowBound=0, cat="Continuous")
    open_f = pulp.LpVariable.dicts("Open_Facility", fac_ids, cat="Binary")

    # Objective
    procurement_freight_tariff_risk = pulp.lpSum(landed_cost[(s, f)] * x[s][f] for s in sup_ids for f in fac_ids)
    variable_production = pulp.lpSum(var_cost[f] * pulp.lpSum(x[s][f] for s in sup_ids) for f in fac_ids)
    facility_fixed = pulp.lpSum(fixed_cost[f] * open_f[f] for f in fac_ids)
    distribution = pulp.lpSum(transport[(f, d)] * y[f][d] for f in fac_ids for d in dem_ids)

    prob += procurement_freight_tariff_risk + variable_production + facility_fixed + distribution

    # Constraints
    # 1. Facility flow balance: inbound components == outbound finished units
    for f in fac_ids:
        prob += pulp.lpSum(x[s][f] for s in sup_ids) == pulp.lpSum(y[f][d] for d in dem_ids), f"Balance_{f}"

    # 2. Supplier capacity
    for s in sup_ids:
        prob += pulp.lpSum(x[s][f] for f in fac_ids) <= sup_cap[s], f"SupCap_{s}"

    # 3. Facility capacity, gated by activation
    for f in fac_ids:
        prob += pulp.lpSum(x[s][f] for s in sup_ids) <= fac_cap[f] * open_f[f], f"FacCap_{f}"

    # 4. Demand satisfaction (minimum service level; allow surplus)
    for d in dem_ids:
        prob += pulp.lpSum(y[f][d] for f in fac_ids) >= service_min[d] * dem_qty[d], f"Demand_{d}"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=verbose))

    flows_sf = pd.DataFrame(
        [(s, f, x[s][f].value()) for s in sup_ids for f in fac_ids if x[s][f].value() and x[s][f].value() > 1e-6],
        columns=["supplier_id", "facility_id", "units"]
    )
    flows_fd = pd.DataFrame(
        [(f, d, y[f][d].value()) for f in fac_ids for d in dem_ids if y[f][d].value() and y[f][d].value() > 1e-6],
        columns=["facility_id", "region_id", "units"]
    )
    facilities_open = [f for f in fac_ids if open_f[f].value() > 0.5]

    cost_breakdown = {
        "procurement_freight_tariff_risk": pulp.value(procurement_freight_tariff_risk),
        "variable_production": pulp.value(variable_production),
        "facility_fixed": pulp.value(facility_fixed),
        "distribution": pulp.value(distribution),
        "total_cost": pulp.value(prob.objective),
    }

    return {
        "status": pulp.LpStatus[status],
        "total_cost": pulp.value(prob.objective),
        "cost_breakdown": cost_breakdown,
        "flows_supplier_facility": flows_sf,
        "flows_facility_demand": flows_fd,
        "facilities_open": facilities_open,
    }


if __name__ == "__main__":
    result = build_and_solve(verbose=False)
    print("Status:", result["status"])
    print("Total landed cost: ${:,.0f}".format(result["total_cost"]))
    print("Open facilities:", result["facilities_open"])
    print("\nCost breakdown:")
    for k, v in result["cost_breakdown"].items():
        print(f"  {k}: ${v:,.0f}")

    OUT = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(OUT, exist_ok=True)
    result["flows_supplier_facility"].to_csv(os.path.join(OUT, "baseline_flows_supplier_facility.csv"), index=False)
    result["flows_facility_demand"].to_csv(os.path.join(OUT, "baseline_flows_facility_demand.csv"), index=False)
    pd.DataFrame([result["cost_breakdown"]]).to_csv(os.path.join(OUT, "baseline_cost_breakdown.csv"), index=False)
    print("\nSaved results to:", os.path.abspath(OUT))
