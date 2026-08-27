# Supply Chain Optimization for High-End Medical Equipment

**Self Project | May 2025 – July 2025**

## Overview

This project focuses on designing and optimizing a **global supply chain for high-end medical equipment** under real-world operational, financial, regulatory, and geopolitical constraints.

The objective was to develop a mathematical optimization framework that determines cost-effective and reliable sourcing and logistics configurations while accounting for factors such as:

* Supplier selection
* Country-level sourcing
* Transportation and logistics costs
* Tariffs and duties
* Supply risk
* Regulatory constraints
* Capacity limitations
* Demand requirements
* Cross-country sourcing trade-offs

The optimization model was formulated as a **Mixed-Integer Nonlinear Programming (MINLP)** problem and implemented in **Python using Gurobi**. Scenario analysis and predictive modeling were subsequently used to evaluate supply-chain configurations under different uncertain conditions.

---

# Objective

The primary objective was to optimize the global supply chain for high-end medical equipment while balancing **cost, reliability, risk, and regulatory feasibility**.

The project aimed to:

1. Determine optimal supplier-country combinations.
2. Minimize total supply chain cost.
3. Account for transportation and logistics costs.
4. Incorporate tariffs and country-specific costs.
5. Model supplier and country-level risks.
6. Respect supplier capacity and demand constraints.
7. Incorporate regulatory requirements.
8. Evaluate supply-chain resilience under uncertainty.
9. Compare alternative sourcing configurations through scenario analysis.
10. Identify cost-effective and reliable supply configurations.

---

# Problem Statement

Global medical-equipment supply chains involve multiple interconnected decisions.

A typical supply chain may include:

```text
Suppliers
   |
   | Sourcing
   ↓
Manufacturing / Procurement
   |
   | International Transportation
   ↓
Distribution / Import
   |
   | Regulatory & Customs
   ↓
Regional Markets
   |
   ↓
Hospitals / Customers
```

For high-end medical equipment, the lowest-cost supplier is not necessarily the optimal choice.

A sourcing configuration may have:

* Lower procurement cost but higher geopolitical risk.
* Lower transportation cost but higher tariff exposure.
* Higher supplier reliability but greater unit cost.
* Better regulatory compatibility but limited capacity.

Therefore, the optimization problem must consider multiple competing objectives and constraints simultaneously.

---

# Methodology

The overall workflow followed the following structure:

```text
Supply Chain Data
        ↓
Data Preparation
        ↓
Supplier & Country Analysis
        ↓
Cost / Risk Parameter Estimation
        ↓
MINLP Formulation
        ↓
Gurobi Optimization
        ↓
Optimal Supply Configuration
        ↓
Scenario Analysis
        ↓
Sensitivity & Risk Analysis
        ↓
Decision Support
```

---

# 1. Data Preparation

Supply chain parameters were defined for suppliers, countries, transportation routes, and demand markets.

The model incorporated information such as:

* Supplier capacity
* Procurement cost
* Transportation cost
* Tariff rates
* Country-level risk
* Supplier reliability
* Regulatory compatibility
* Demand requirements
* Lead-time considerations

The data was structured to allow different supply-chain configurations to be evaluated systematically.

---

# 2. Supply Chain Network

The model represents the supply chain as a network connecting suppliers with demand locations.

A simplified representation is:

```text
             Supplier 1
             /        \
            /          \
       Supplier 2     Supplier 3
            \            /
             \          /
              ↓        ↓
          Distribution
               |
               ↓
        Demand Markets
```

Each potential sourcing route has associated costs, risks, and feasibility constraints.

The optimization determines which suppliers and routes should be selected and how much demand should be allocated to each.

---

# 3. Decision Variables

The optimization model uses decision variables to represent sourcing and allocation decisions.

For example:

### Continuous Variables

Let:

$$
x_{ij}
$$

represent the quantity of medical equipment sourced from supplier \(i\) and allocated to market \(j\).

### Binary Variables

Let:

$$
y_i \in \{0,1\}
$$

represent whether supplier \(i\) is selected.

The binary variables allow the model to capture discrete supplier-selection decisions, while continuous variables determine quantities allocated across the supply chain.

---

# 4. Objective Function

The primary objective was to minimize the overall supply chain cost while accounting for multiple cost components.

A simplified formulation is:

$$
\min Z =
C_{procurement}
+
C_{transportation}
+
C_{tariff}
+
C_{inventory}
+
C_{risk}
$$

where:

* \(C_{procurement}\) = procurement/sourcing cost
* \(C_{transportation}\) = logistics and transportation cost
* \(C_{tariff}\) = tariffs and duties
* \(C_{inventory}\) = inventory-related cost
* \(C_{risk}\) = risk-related cost or penalty

Depending on the scenario, risk and reliability factors were incorporated into the objective function or represented through additional constraints.

---

# 5. Supply Constraints

Supplier capacity constraints ensure that the model does not allocate more equipment than a supplier can provide.

For supplier \(i\):

$$
\sum_j x_{ij} \leq Capacity_i
$$

This ensures that:

$$
Supply_i \leq Capacity_i
$$

for every supplier.

---

# 6. Demand Constraints

The model must satisfy the required demand for each market.

For demand location \(j\):

$$
\sum_i x_{ij} \geq Demand_j
$$

This ensures that the optimized supply configuration provides sufficient equipment to meet market requirements.

---

# 7. Supplier Selection Constraints

Binary supplier-selection variables were linked to sourcing quantities.

A typical constraint is:

$$
x_{ij} \leq Capacity_i y_i
$$

where:

* \(x_{ij}\) = quantity sourced
* \(Capacity_i\) = supplier capacity
* \(y_i\) = supplier selection variable

If:

$$
y_i=0
$$

the model cannot allocate equipment from that supplier.

If:

$$
y_i=1
$$

the supplier becomes available for sourcing.

---

# 8. Tariff Modeling

International sourcing introduces country-specific tariffs and duties.

The tariff cost can be represented as:

$$
C_{tariff} =
\sum_{i,j}
x_{ij} \cdot P_i \cdot T_{ij}
$$

where:

* \(P_i\) = applicable product/procurement value
* \(T_{ij}\) = tariff rate between sourcing country \(i\) and destination \(j\)

This allows the optimization to consider the financial impact of international trade policies.

---

# 9. Risk Modeling

Supply chain risk was incorporated into the optimization framework to prevent the model from selecting configurations based solely on minimum cost.

Potential risk factors include:

* Geopolitical risk
* Supplier reliability
* Country risk
* Transportation disruption
* Regulatory uncertainty
* Supply interruption probability

A simplified risk penalty can be represented as:

$$
C_{risk} =
\sum_{i,j}x_{ij}R_{ij}
$$

where \(R_{ij}\) represents the risk associated with sourcing from supplier \(i\) to market \(j\).

This enables a trade-off between **low cost and high reliability**.

---

# 10. Regulatory Constraints

Medical equipment is subject to regulatory requirements that can restrict sourcing options.

The model incorporated regulatory feasibility constraints to ensure that selected sourcing configurations satisfy applicable requirements.

A simplified binary feasibility constraint can be represented as:

$$
x_{ij} \leq M R_{ij}
$$

where:

* \(R_{ij}=1\) indicates that the route/configuration is regulatory-compliant.
* \(R_{ij}=0\) indicates that the route is not feasible.
* \(M\) is a sufficiently large constant.

This prevents the optimizer from selecting infeasible supply routes.

---

# 11. Mixed-Integer Nonlinear Programming

The supply chain problem was formulated as a **Mixed-Integer Nonlinear Programming (MINLP)** model.

The formulation combines:

### Continuous Decisions

Such as:

* Quantity sourced
* Shipment allocation
* Flow through routes

### Integer/Binary Decisions

Such as:

* Supplier selection
* Facility/route activation
* Strategic sourcing decisions

### Nonlinear Relationships

Nonlinearities can arise from:

* Risk functions
* Cost interactions
* Capacity utilization
* Penalty functions
* Scenario-dependent relationships

The combination of these characteristics makes MINLP suitable for representing complex supply-chain decisions.

---

# 12. Gurobi Optimization

The optimization model was implemented in Python using **Gurobi**.

A simplified modeling workflow is:

```python
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("SupplyChainOptimization")

# Decision variables
x = model.addVars(
    suppliers,
    markets,
    lb=0,
    vtype=GRB.CONTINUOUS,
    name="flow"
)

y = model.addVars(
    suppliers,
    vtype=GRB.BINARY,
    name="supplier_selected"
)

# Objective
model.setObjective(
    total_cost,
    GRB.MINIMIZE
)

# Constraints
# Demand constraints
# Capacity constraints
# Supplier selection constraints
# Tariff constraints
# Regulatory constraints
# Risk constraints

model.optimize()
```

Gurobi was used to solve the mathematical optimization problem and identify feasible high-quality supply-chain configurations.

---

# 13. Scenario Analysis

A major component of the project was **scenario analysis**.

Instead of evaluating the supply chain under only one set of assumptions, multiple scenarios were considered to understand how the optimal strategy changes under uncertainty.

Potential scenarios include:

| Scenario            | Description                          |
| ------------------- | ------------------------------------ |
| Base Case           | Normal operating conditions          |
| High Tariff         | Increased international tariff rates |
| Supply Disruption   | Reduced supplier availability        |
| High Logistics Cost | Increased transportation costs       |
| High Risk           | Increased geopolitical/supplier risk |
| Capacity Reduction  | Lower supplier capacity              |
| Demand Increase     | Higher market demand                 |

For each scenario, the optimization model can be re-run and the resulting supply configuration compared.

---

# 14. Predictive Modeling Under Uncertainty

Predictive modeling was incorporated to evaluate how changing conditions could influence supply-chain decisions.

Potential uncertain parameters include:

* Demand
* Transportation costs
* Supplier reliability
* Tariff rates
* Lead times
* Disruption probability

The general framework can be represented as:

```text
Historical / Assumed Data
          ↓
Parameter Estimation
          ↓
Scenario Generation
          ↓
Optimization Model
          ↓
Supply Configuration
          ↓
Cost & Risk Evaluation
```

This approach allows the model to move beyond static optimization toward **decision-making under uncertainty**.

---

# 15. Scenario Comparison

Each scenario was evaluated using multiple decision criteria.

Key outputs include:

* Total supply chain cost
* Procurement cost
* Transportation cost
* Tariff cost
* Risk exposure
* Supplier utilization
* Market allocation
* Number of active suppliers
* Feasibility of the configuration

A simplified comparison framework is:

| Scenario            | Total Cost |      Risk | Supplier Count | Feasibility |
| ------------------- | ---------: | --------: | -------------: | ----------- |
| Base Case           |  Evaluated | Evaluated |      Evaluated | Feasible    |
| High Tariff         |  Evaluated | Evaluated |      Evaluated | Feasible    |
| Supply Disruption   |  Evaluated | Evaluated |      Evaluated | Evaluated   |
| High Logistics Cost |  Evaluated | Evaluated |      Evaluated | Evaluated   |
| High Risk           |  Evaluated | Evaluated |      Evaluated | Evaluated   |

---

# Results

The optimization framework enabled **data-driven evaluation of global supply-chain configurations** and identified sourcing strategies that balance cost, reliability, and risk.

The analysis demonstrated that the lowest-cost configuration is not always the most desirable configuration once factors such as tariffs, supplier risk, logistics costs, and regulatory restrictions are considered.

The scenario-based approach allowed alternative supply-chain configurations to be compared under changing operating conditions.

Key outcomes included:

* Identification of cost-effective sourcing configurations.
* Evaluation of supplier allocation decisions.
* Integration of transportation and tariff costs.
* Incorporation of supplier and country-level risk.
* Enforcement of regulatory and operational constraints.
* Comparison of alternative supply-chain scenarios.
* Evaluation of trade-offs between cost and reliability.
* Development of a data-driven decision-support framework.

---

# Key Findings

## 1. Cost optimization alone can be misleading

A sourcing strategy based purely on procurement cost can overlook tariffs, transportation costs, supply risk, and regulatory requirements.

The optimization framework considers these factors simultaneously.

## 2. Supplier diversification can improve resilience

Depending on the scenario, distributing sourcing across multiple suppliers can reduce dependence on a single supplier and improve resilience against supply disruptions.

However, diversification may increase procurement or logistics costs.

## 3. Tariffs can significantly influence sourcing decisions

Changes in tariff rates can alter the relative attractiveness of sourcing countries and shift the optimal supply configuration.

## 4. Risk creates a cost-reliability trade-off

A lower-cost supplier may have higher supply risk, while a more reliable supplier may have higher procurement or transportation costs.

The optimization framework explicitly evaluates this trade-off.

## 5. Scenario analysis improves decision-making

Testing multiple scenarios provides greater insight than optimizing for a single assumed future state.

It allows decision-makers to identify configurations that remain effective under changing conditions.

---

# Trade-Off Analysis

The project focuses on balancing several competing objectives:

```text
                     Reliability
                         ↑
                         |
                         |
                         |       ● Robust Configuration
                         |
                         |
                         |
                         └──────────────────→
                              Cost
```

The ideal solution is not necessarily the configuration with minimum cost.

Instead, a robust solution should provide an appropriate balance between:

$$
Cost \leftrightarrow Risk \leftrightarrow Reliability
$$

while satisfying:

$$
Demand,\ Capacity,\ Regulatory,\ Operational
$$

constraints.

---

# Decision-Support Framework

The final framework can support strategic supply-chain decisions through:

```text
                   Input Parameters
                         ↓
              ┌─────────────────────┐
              │ Supply Chain Model  │
              └─────────────────────┘
                         ↓
                  Optimization
                         ↓
              Optimal Configuration
                         ↓
              Scenario Evaluation
                         ↓
          ┌──────────────┴──────────────┐
          ↓                             ↓
      Cost Analysis                Risk Analysis
          ↓                             ↓
          └──────────────┬──────────────┘
                         ↓
                  Final Decision
```

This provides a structured way to evaluate sourcing strategies before implementation.

---

# Project Structure

A recommended repository structure is:

```text
Supply-Chain-Optimization/
│
├── data/
│   ├── suppliers.csv
│   ├── demand.csv
│   ├── transportation.csv
│   ├── tariffs.csv
│   └── risk_parameters.csv
│
├── notebooks/
│   ├── 01_Data_Preparation.ipynb
│   ├── 02_Supply_Chain_Analysis.ipynb
│   ├── 03_MINLP_Model.ipynb
│   ├── 04_Optimization.ipynb
│   └── 05_Scenario_Analysis.ipynb
│
├── src/
│   ├── data_processing.py
│   ├── cost_model.py
│   ├── risk_model.py
│   ├── optimization.py
│   └── scenario_analysis.py
│
├── results/
│   ├── optimal_solution.csv
│   ├── scenario_results.csv
│   └── visualizations/
│
├── requirements.txt
│
└── README.md
```

---

# Technologies Used

| Technology                          | Purpose                        |
| ----------------------------------- | ------------------------------ |
| Python                              | Model development and analysis |
| Gurobi                              | Mathematical optimization      |
| Pandas                              | Data manipulation              |
| NumPy                               | Numerical computation          |
| Matplotlib                          | Data visualization             |
| Seaborn                             | Statistical visualization      |
| Jupyter Notebook                    | Interactive analysis           |
| Mixed-Integer Nonlinear Programming | Supply-chain optimization      |
| Scenario Analysis                   | Uncertainty evaluation         |

---

# Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/Supply-Chain-Optimization.git
```

Navigate to the project directory:

```bash
cd Supply-Chain-Optimization
```

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

Launch Jupyter Notebook:

```bash
jupyter notebook
```

Open the notebooks inside the `notebooks/` directory to reproduce the analysis.

---

# Requirements

Example `requirements.txt`:

```text
numpy
pandas
matplotlib
seaborn
scipy
jupyter
gurobipy
```

A valid Gurobi installation/license may be required to execute the optimization model.

---

# Reproducibility

The analysis can be reproduced using the following workflow:

1. Load supplier, demand, transportation, tariff, and risk data.
2. Clean and preprocess the datasets.
3. Define supply-chain parameters.
4. Construct decision variables.
5. Formulate the MINLP objective function.
6. Add capacity and demand constraints.
7. Add supplier-selection constraints.
8. Incorporate tariffs and logistics costs.
9. Add risk and regulatory constraints.
10. Solve the optimization model using Gurobi.
11. Extract the optimal supply-chain configuration.
12. Generate alternative scenarios.
13. Re-optimize under each scenario.
14. Compare cost, risk, reliability, and feasibility.
15. Identify robust supply-chain configurations.

---

# Recommended Visualizations

The repository can include the following visualizations to make the analysis easier to interpret.

## 1. Supply Chain Network

Visualize suppliers, countries, routes, and demand markets.

## 2. Supplier Allocation

Show the percentage of total demand allocated to each supplier.

## 3. Cost Breakdown

Compare:

```text
Total Cost
├── Procurement Cost
├── Transportation Cost
├── Tariff Cost
├── Inventory Cost
└── Risk Cost
```

## 4. Scenario Comparison

Compare total cost and risk across different scenarios.

## 5. Supplier Utilization

Visualize the percentage utilization of each supplier's available capacity.

## 6. Risk-Cost Frontier

Plot alternative supply configurations based on:

* Total cost
* Risk exposure

This helps identify configurations that offer favorable cost-risk trade-offs.

---

# Future Improvements

The model can be extended in several directions.

## 1. Stochastic Optimization

Replace deterministic scenario assumptions with probability distributions for uncertain parameters such as demand, tariffs, and disruption risk.

## 2. Robust Optimization

Develop a robust optimization formulation that remains feasible under worst-case or bounded uncertainty.

## 3. Multi-Objective Optimization

Simultaneously optimize:

* Cost
* Risk
* Reliability
* Lead time
* Resilience

and generate a Pareto frontier of alternative solutions.

## 4. Real-Time Data Integration

Integrate live information on:

* Freight rates
* Tariff changes
* Supplier performance
* Geopolitical risk
* Demand forecasts

to dynamically update the optimization model.

## 5. Machine Learning-Based Forecasting

Use machine learning models to forecast:

* Demand
* Transportation costs
* Supplier delays
* Disruption probability
* Lead times

and feed these predictions into the optimization framework.

## 6. Supply Chain Resilience

Extend the model to explicitly measure resilience through:

* Recovery time
* Disruption scenarios
* Supplier redundancy
* Alternative sourcing routes
* Service-level constraints

---

# Key Concepts Demonstrated

This project demonstrates practical application of:

* Operations Research
* Supply Chain Optimization
* Mathematical Programming
* Mixed-Integer Nonlinear Programming
* Gurobi Optimization
* Supplier Selection
* Network Optimization
* Logistics Optimization
* Risk Modeling
* Tariff Modeling
* Regulatory Constraints
* Scenario Analysis
* Predictive Modeling
* Decision-Making Under Uncertainty
* Supply Chain Resilience
* Cost-Risk Trade-off Analysis

---

# Conclusion

The project developed a quantitative framework for optimizing a global supply chain for high-end medical equipment under realistic operational and external constraints.

By combining **MINLP optimization, Gurobi, risk modeling, tariff considerations, regulatory constraints, and scenario analysis**, the framework enables systematic comparison of alternative sourcing and logistics configurations.

The analysis demonstrates how mathematical optimization can support supply-chain decisions by moving beyond simple cost minimization toward a more comprehensive evaluation of **cost, risk, reliability, and resilience**.

