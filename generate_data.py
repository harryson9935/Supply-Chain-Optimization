"""
generate_data.py
-----------------
Generates a synthetic-but-realistic dataset for a global high-end medical
equipment supply chain (e.g., MRI/CT scanner components, dialysis machines,
surgical robotics sub-assemblies).

Entities:
    Suppliers        -> raw materials / precision components (upstream)
    Facilities        -> assembly / manufacturing plants (midstream)
    Distribution Ctrs -> regional demand nodes / hospital-network hubs (downstream)

All numbers are illustrative (grounded in plausible ranges for freight,
tariffs, and component costs) so the model and pipeline are fully
reproducible without needing proprietary data.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------
# 1. SUPPLIERS  (precision components: sensors, magnets, semiconductors,
#    optics, chassis/casings)
# ---------------------------------------------------------------------
suppliers = pd.DataFrame([
    {"supplier_id": "S1", "name": "Nordic Precision Components", "country": "Germany",   "component": "Superconducting Magnets", "capacity_units": 1200, "unit_cost_usd": 8400, "lead_time_days": 21, "risk_score": 0.12},
    {"supplier_id": "S2", "name": "Rhine Semicon Labs",          "country": "Germany",   "component": "Imaging Sensors",         "capacity_units": 3000, "unit_cost_usd": 2100, "lead_time_days": 14, "risk_score": 0.10},
    {"supplier_id": "S3", "name": "Kansai Optics Corp",          "country": "Japan",     "component": "Precision Optics",        "capacity_units": 2500, "unit_cost_usd": 1650, "lead_time_days": 18, "risk_score": 0.15},
    {"supplier_id": "S4", "name": "Shenzhen MedTech Fab",        "country": "China",     "component": "PCB Assemblies",          "capacity_units": 5000, "unit_cost_usd": 640,  "lead_time_days": 25, "risk_score": 0.35},
    {"supplier_id": "S5", "name": "Suzhou Alloy Works",          "country": "China",     "component": "Chassis / Casings",       "capacity_units": 4200, "unit_cost_usd": 480,  "lead_time_days": 22, "risk_score": 0.33},
    {"supplier_id": "S6", "name": "Bengaluru Semitech",          "country": "India",     "component": "Imaging Sensors",         "capacity_units": 2800, "unit_cost_usd": 1750, "lead_time_days": 16, "risk_score": 0.22},
    {"supplier_id": "S7", "name": "Pune Precision Tools",        "country": "India",     "component": "PCB Assemblies",          "capacity_units": 3600, "unit_cost_usd": 700,  "lead_time_days": 19, "risk_score": 0.20},
    {"supplier_id": "S8", "name": "Minnesota Medical Materials", "country": "USA",       "component": "Superconducting Magnets", "capacity_units": 900,  "unit_cost_usd": 9600, "lead_time_days": 10, "risk_score": 0.08},
    {"supplier_id": "S9", "name": "Ohio Alloy & Casing",         "country": "USA",       "component": "Chassis / Casings",       "capacity_units": 2600, "unit_cost_usd": 610,  "lead_time_days": 9,  "risk_score": 0.07},
    {"supplier_id": "S10","name": "Seoul Optics & Sensors",      "country": "S. Korea",  "component": "Precision Optics",        "capacity_units": 2200, "unit_cost_usd": 1580, "lead_time_days": 15, "risk_score": 0.14},
])

# ---------------------------------------------------------------------
# 2. MANUFACTURING / ASSEMBLY FACILITIES
# ---------------------------------------------------------------------
facilities = pd.DataFrame([
    {"facility_id": "F1", "name": "Rotterdam Assembly Plant",   "country": "Netherlands", "capacity_units": 2200, "fixed_cost_usd": 480000, "variable_cost_per_unit": 950, "regulatory_index": 0.95},
    {"facility_id": "F2", "name": "Monterrey Assembly Plant",   "country": "Mexico",      "capacity_units": 2600, "fixed_cost_usd": 310000, "variable_cost_per_unit": 620, "regulatory_index": 0.80},
    {"facility_id": "F3", "name": "Chennai Assembly Plant",     "country": "India",       "capacity_units": 3000, "fixed_cost_usd": 260000, "variable_cost_per_unit": 540, "regulatory_index": 0.78},
    {"facility_id": "F4", "name": "Ohio Assembly Plant",        "country": "USA",         "capacity_units": 2000, "fixed_cost_usd": 610000, "variable_cost_per_unit": 1120,"regulatory_index": 0.98},
    {"facility_id": "F5", "name": "Bangkok Assembly Plant",     "country": "Thailand",    "capacity_units": 2400, "fixed_cost_usd": 275000, "variable_cost_per_unit": 580, "regulatory_index": 0.82},
])

# ---------------------------------------------------------------------
# 3. DEMAND / DISTRIBUTION REGIONS (hospital-network hubs)
# ---------------------------------------------------------------------
demand = pd.DataFrame([
    {"region_id": "D1", "name": "North America",     "demand_units": 1400, "service_level_min": 0.97},
    {"region_id": "D2", "name": "Western Europe",     "demand_units": 1250, "service_level_min": 0.97},
    {"region_id": "D3", "name": "East Asia",          "demand_units": 1600, "service_level_min": 0.95},
    {"region_id": "D4", "name": "South Asia",         "demand_units": 900,  "service_level_min": 0.93},
    {"region_id": "D5", "name": "Middle East",        "demand_units": 550,  "service_level_min": 0.94},
    {"region_id": "D6", "name": "Latin America",      "demand_units": 700,  "service_level_min": 0.93},
])

# ---------------------------------------------------------------------
# 4. SUPPLIER -> FACILITY TRANSPORT COST ($/unit) and TARIFFS (%)
# ---------------------------------------------------------------------
sup_ids = suppliers["supplier_id"].tolist()
fac_ids = facilities["facility_id"].tolist()

# Base freight cost roughly reflects geographic distance/logistics complexity
freight_base = {
    ("S1","F1"):180, ("S1","F2"):950, ("S1","F3"):1200, ("S1","F4"):980, ("S1","F5"):1350,
    ("S2","F1"):160, ("S2","F2"):920, ("S2","F3"):1150, ("S2","F4"):940, ("S2","F5"):1300,
    ("S3","F1"):1400, ("S3","F2"):1550, ("S3","F3"):820,  ("S3","F4"):1100,("S3","F5"):650,
    ("S4","F1"):980,  ("S4","F2"):1050,("S4","F3"):420,   ("S4","F4"):1250,("S4","F5"):380,
    ("S5","F1"):1020, ("S5","F2"):1080,("S5","F3"):450,   ("S5","F4"):1280,("S5","F5"):400,
    ("S6","F1"):1150, ("S6","F2"):1500,("S6","F3"):180,   ("S6","F4"):1400,("S6","F5"):620,
    ("S7","F1"):1180, ("S7","F2"):1520,("S7","F3"):160,   ("S7","F4"):1420,("S7","F5"):640,
    ("S8","F1"):880,  ("S8","F2"):420, ("S8","F3"):1450,  ("S8","F4"):180, ("S8","F5"):1500,
    ("S9","F1"):900,  ("S9","F2"):400, ("S9","F3"):1480,  ("S9","F4"):160, ("S9","F5"):1520,
    ("S10","F1"):1300,("S10","F2"):1600,("S10","F3"):720, ("S10","F4"):1250,("S10","F5"):580,
}

# Tariff rate (%) applied on landed component value, by (supplier_country -> facility_country) trade lane
tariff_lookup = {
    ("Germany","Netherlands"):0.00, ("Germany","Mexico"):0.05, ("Germany","India"):0.07, ("Germany","USA"):0.08, ("Germany","Thailand"):0.06,
    ("Japan","Netherlands"):0.03,   ("Japan","Mexico"):0.04,   ("Japan","India"):0.09,   ("Japan","USA"):0.02,   ("Japan","Thailand"):0.05,
    ("China","Netherlands"):0.06,   ("China","Mexico"):0.10,   ("China","India"):0.12,   ("China","USA"):0.25,   ("China","Thailand"):0.04,
    ("India","Netherlands"):0.04,   ("India","Mexico"):0.06,   ("India","India"):0.00,   ("India","USA"):0.06,   ("India","Thailand"):0.05,
    ("USA","Netherlands"):0.03,     ("USA","Mexico"):0.00,     ("USA","India"):0.10,     ("USA","USA"):0.00,     ("USA","Thailand"):0.06,
    ("S. Korea","Netherlands"):0.03,("S. Korea","Mexico"):0.05,("S. Korea","India"):0.08,("S. Korea","USA"):0.03,("S. Korea","Thailand"):0.04,
}

rows = []
sup_country = dict(zip(suppliers.supplier_id, suppliers.country))
fac_country = dict(zip(facilities.facility_id, facilities.country))
for s in sup_ids:
    for f in fac_ids:
        freight = freight_base[(s, f)]
        tariff = tariff_lookup[(sup_country[s], fac_country[f])]
        rows.append({"supplier_id": s, "facility_id": f, "freight_cost_per_unit": freight, "tariff_rate": tariff})
sup_fac_cost = pd.DataFrame(rows)

# ---------------------------------------------------------------------
# 5. FACILITY -> DEMAND REGION TRANSPORT COST ($/unit)
# ---------------------------------------------------------------------
dist_ids = demand["region_id"].tolist()
fac_to_demand_base = {
    ("F1","D1"):1450, ("F1","D2"):210,  ("F1","D3"):1600, ("F1","D4"):1750, ("F1","D5"):1200, ("F1","D6"):1900,
    ("F2","D1"):380,  ("F2","D2"):1550, ("F2","D3"):1950, ("F2","D4"):2100, ("F2","D5"):1850, ("F2","D6"):520,
    ("F3","D1"):1850, ("F3","D2"):1400, ("F3","D3"):620,  ("F3","D4"):280,  ("F3","D5"):950,  ("F3","D6"):2050,
    ("F4","D1"):160,  ("F4","D2"):1350, ("F4","D3"):1850, ("F4","D4"):2000, ("F4","D5"):1700, ("F4","D6"):980,
    ("F5","D1"):1900, ("F5","D2"):1550, ("F5","D3"):480,  ("F5","D4"):620,  ("F5","D5"):1150, ("F5","D6"):2150,
}
rows2 = []
for f in fac_ids:
    for d in dist_ids:
        rows2.append({"facility_id": f, "region_id": d, "transport_cost_per_unit": fac_to_demand_base[(f, d)]})
fac_demand_cost = pd.DataFrame(rows2)

# Save all datasets
suppliers.to_csv(os.path.join(OUT, "suppliers.csv"), index=False)
facilities.to_csv(os.path.join(OUT, "facilities.csv"), index=False)
demand.to_csv(os.path.join(OUT, "demand.csv"), index=False)
sup_fac_cost.to_csv(os.path.join(OUT, "supplier_facility_cost.csv"), index=False)
fac_demand_cost.to_csv(os.path.join(OUT, "facility_demand_cost.csv"), index=False)

print("Datasets generated in:", os.path.abspath(OUT))
for f in ["suppliers.csv","facilities.csv","demand.csv","supplier_facility_cost.csv","facility_demand_cost.csv"]:
    print(" -", f)
