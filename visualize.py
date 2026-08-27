"""
visualize.py
------------
Generates all figures for the README / report:
    1. network_flow_diagram.png   - supplier -> facility -> region flows (baseline)
    2. cost_breakdown.png         - baseline cost component pie/bar
    3. scenario_comparison.png    - total cost across scenarios (bar)
    4. supplier_utilization.png   - heatmap of supplier capacity utilization
    5. facility_utilization.png   - facility throughput vs capacity
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
FIG = os.path.join(RESULTS, "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 10,
})

COLOR_SUPPLIER = "#2E86AB"
COLOR_FACILITY = "#F6A800"
COLOR_DEMAND = "#4CAF50"


def fig1_network_diagram():
    suppliers = pd.read_csv(os.path.join(DATA, "suppliers.csv"))
    facilities = pd.read_csv(os.path.join(DATA, "facilities.csv"))
    demand = pd.read_csv(os.path.join(DATA, "demand.csv"))
    flows_sf = pd.read_csv(os.path.join(RESULTS, "baseline_flows_supplier_facility.csv"))
    flows_fd = pd.read_csv(os.path.join(RESULTS, "baseline_flows_facility_demand.csv"))

    G = nx.DiGraph()
    for _, r in suppliers.iterrows():
        G.add_node(r.supplier_id, layer=0, label=f"{r.supplier_id}\n{r.country}")
    for _, r in facilities.iterrows():
        G.add_node(r.facility_id, layer=1, label=f"{r.facility_id}\n{r.country}")
    for _, r in demand.iterrows():
        G.add_node(r.region_id, layer=2, label=f"{r.region_id}\n{r['name']}")

    for _, r in flows_sf.iterrows():
        G.add_edge(r.supplier_id, r.facility_id, weight=r.units)
    for _, r in flows_fd.iterrows():
        G.add_edge(r.facility_id, r.region_id, weight=r.units)

    pos = {}
    sup_ids = suppliers.supplier_id.tolist()
    fac_ids = facilities.facility_id.tolist()
    dem_ids = demand.region_id.tolist()
    for i, n in enumerate(sup_ids):
        pos[n] = (0, -i * (10 / max(len(sup_ids)-1, 1)) + 5)
    for i, n in enumerate(fac_ids):
        pos[n] = (1, -i * (10 / max(len(fac_ids)-1, 1)) + 5)
    for i, n in enumerate(dem_ids):
        pos[n] = (2, -i * (10 / max(len(dem_ids)-1, 1)) + 5)

    fig, ax = plt.subplots(figsize=(14, 9))

    active_sf = [(u, v) for u, v, d in G.edges(data=True) if u in sup_ids]
    active_fd = [(u, v) for u, v, d in G.edges(data=True) if u in fac_ids]

    max_w = max([G[u][v]["weight"] for u, v in G.edges()]) if G.edges() else 1
    for u, v in active_sf:
        w = G[u][v]["weight"]
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=0.5 + 4*w/max_w,
                                edge_color=COLOR_SUPPLIER, alpha=0.5, ax=ax,
                                connectionstyle="arc3,rad=0.05", arrows=True, arrowsize=8)
    for u, v in active_fd:
        w = G[u][v]["weight"]
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=0.5 + 4*w/max_w,
                                edge_color=COLOR_FACILITY, alpha=0.55, ax=ax,
                                connectionstyle="arc3,rad=0.05", arrows=True, arrowsize=8)

    nx.draw_networkx_nodes(G, pos, nodelist=sup_ids, node_color=COLOR_SUPPLIER,
                            node_size=900, ax=ax, edgecolors="white", linewidths=1.5)
    open_fac = [f for f in fac_ids if f in [e[1] for e in active_sf]]
    closed_fac = [f for f in fac_ids if f not in open_fac]
    nx.draw_networkx_nodes(G, pos, nodelist=open_fac, node_color=COLOR_FACILITY,
                            node_size=1300, ax=ax, edgecolors="white", linewidths=1.5)
    nx.draw_networkx_nodes(G, pos, nodelist=closed_fac, node_color="#D9D9D9",
                            node_size=1000, ax=ax, edgecolors="white", linewidths=1.5)
    nx.draw_networkx_nodes(G, pos, nodelist=dem_ids, node_color=COLOR_DEMAND,
                            node_size=1100, ax=ax, edgecolors="white", linewidths=1.5)

    labels = {n: G.nodes[n]["label"] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight="bold", ax=ax)

    ax.text(0, 11.5, "SUPPLIERS", ha="center", fontsize=13, fontweight="bold", color=COLOR_SUPPLIER)
    ax.text(1, 11.5, "ASSEMBLY FACILITIES", ha="center", fontsize=13, fontweight="bold", color="#B8790A")
    ax.text(2, 11.5, "DEMAND REGIONS", ha="center", fontsize=13, fontweight="bold", color=COLOR_DEMAND)
    ax.set_title("Optimal Global Supply Chain Flow — Baseline Scenario\n(edge width \u221d shipped volume; grey = inactive facility)",
                  fontsize=13, fontweight="bold", pad=20)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "network_flow_diagram.png"), dpi=160, bbox_inches="tight")
    plt.close()
    print("Saved network_flow_diagram.png")


def fig2_cost_breakdown():
    df = pd.read_csv(os.path.join(RESULTS, "baseline_cost_breakdown.csv"))
    labels = ["Procurement +\nFreight + Tariff + Risk", "Facility Variable\nProduction", "Facility Fixed\n(Activation)", "Distribution\n(Facility\u2192Region)"]
    values = [df["procurement_freight_tariff_risk"][0], df["variable_production"][0], df["facility_fixed"][0], df["distribution"][0]]
    colors = ["#2E86AB", "#F6A800", "#C0392B", "#4CAF50"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    axes[0].pie(values, labels=labels, autopct=lambda p: f"${p*sum(values)/100:,.0f}\n({p:.1f}%)",
                colors=colors, startangle=90, textprops={"fontsize": 9})
    axes[0].set_title("Baseline Total Landed Cost Breakdown\n(Total: ${:,.0f})".format(sum(values)), fontweight="bold")

    bars = axes[1].bar(labels, values, color=colors)
    axes[1].set_ylabel("Cost (USD)")
    axes[1].set_title("Cost Components", fontweight="bold")
    axes[1].tick_params(axis='x', rotation=15)
    for b, v in zip(bars, values):
        axes[1].text(b.get_x() + b.get_width()/2, v, f"${v:,.0f}", ha="center", va="bottom", fontsize=8)
    axes[1].spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "cost_breakdown.png"), dpi=160, bbox_inches="tight")
    plt.close()
    print("Saved cost_breakdown.png")


def fig3_scenario_comparison():
    df = pd.read_csv(os.path.join(RESULTS, "scenario_comparison.csv"))
    df = df.sort_values("total_cost")

    fig, ax = plt.subplots(figsize=(11, 6))
    colors = ["#4CAF50" if s == "Baseline" else "#C0392B" if pct > 10 else "#F6A800"
              for s, pct in zip(df.scenario, df.pct_change_vs_baseline)]
    bars = ax.barh(df.scenario, df.total_cost, color=colors)
    for b, v, pct in zip(bars, df.total_cost, df.pct_change_vs_baseline):
        label = f"${v:,.0f}" + (f"  ({pct:+.1f}%)" if pct != 0 else "  (baseline)")
        ax.text(v, b.get_y() + b.get_height()/2, "  " + label, va="center", fontsize=9)

    ax.set_xlabel("Total Landed Cost (USD)")
    ax.set_title("Total Optimized Cost Across Scenarios\n(data-driven scenario analysis under uncertainty)", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, df.total_cost.max() * 1.28)

    legend_handles = [
        mpatches.Patch(color="#4CAF50", label="Baseline"),
        mpatches.Patch(color="#F6A800", label="Moderate impact (\u226410%)"),
        mpatches.Patch(color="#C0392B", label="High impact (>10%)"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "scenario_comparison.png"), dpi=160, bbox_inches="tight")
    plt.close()
    print("Saved scenario_comparison.png")


def fig4_supplier_utilization():
    suppliers = pd.read_csv(os.path.join(DATA, "suppliers.csv"))
    flows_sf = pd.read_csv(os.path.join(RESULTS, "baseline_flows_supplier_facility.csv"))

    used = flows_sf.groupby("supplier_id")["units"].sum().reindex(suppliers.supplier_id).fillna(0)
    cap = suppliers.set_index("supplier_id")["capacity_units"]
    util_pct = (used / cap * 100).round(1)

    fig, ax = plt.subplots(figsize=(10, 6))
    order = util_pct.sort_values(ascending=True)
    colors = plt.cm.RdYlGn_r(order.values / 100)
    bars = ax.barh([f"{sid} ({suppliers.set_index('supplier_id').loc[sid,'country']})" for sid in order.index],
                    order.values, color=colors)
    for b, v in zip(bars, order.values):
        ax.text(v, b.get_y() + b.get_height()/2, f"  {v:.1f}%", va="center", fontsize=9)
    ax.set_xlabel("Capacity Utilization (%)")
    ax.set_title("Supplier Capacity Utilization — Baseline Optimal Solution", fontweight="bold")
    ax.set_xlim(0, 110)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "supplier_utilization.png"), dpi=160, bbox_inches="tight")
    plt.close()
    print("Saved supplier_utilization.png")


def fig5_facility_utilization():
    facilities = pd.read_csv(os.path.join(DATA, "facilities.csv"))
    flows_sf = pd.read_csv(os.path.join(RESULTS, "baseline_flows_supplier_facility.csv"))

    used = flows_sf.groupby("facility_id")["units"].sum().reindex(facilities.facility_id).fillna(0)
    cap = facilities.set_index("facility_id")["capacity_units"]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(facilities))
    w = 0.35
    ax.bar(x - w/2, cap.values, width=w, label="Capacity", color="#D9D9D9")
    ax.bar(x + w/2, used.values, width=w, label="Throughput (Optimal)", color=COLOR_FACILITY)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{fid}\n{facilities.set_index('facility_id').loc[fid,'name']}" for fid in facilities.facility_id],
                        fontsize=8)
    ax.set_ylabel("Units")
    ax.set_title("Facility Capacity vs. Optimal Throughput — Baseline", fontweight="bold")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    for i, (c, u) in enumerate(zip(cap.values, used.values)):
        if u > 0:
            ax.text(i + w/2, u, f"{u:,.0f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "facility_utilization.png"), dpi=160, bbox_inches="tight")
    plt.close()
    print("Saved facility_utilization.png")


if __name__ == "__main__":
    fig1_network_diagram()
    fig2_cost_breakdown()
    fig3_scenario_comparison()
    fig4_supplier_utilization()
    fig5_facility_utilization()
    print("\nAll figures saved to:", os.path.abspath(FIG))
