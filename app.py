"""
Cairo Transportation Management System — Flask API
CSE112 Design and Analysis of Algorithms Project
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, render_template, send_from_directory

from core.graph import CairoGraph
from core.mst import kruskal_mst, prim_mst, analyze_mst
from core.shortest_path import dijkstra, yen_k_shortest
from core.astar import astar_search, compare_dijkstra_vs_astar
from core.dynamic_programming import (
    optimize_transit_schedule, road_maintenance_allocation,
    memoized_route, get_cache_stats
)
from core.greedy import optimize_signals, emergency_preemption, analyze_greedy_optimality
from core.traffic_simulation import simulate_traffic, compare_with_alternate_routes
from bonus.ml_prediction import get_predictor

app = Flask(__name__)

# ─── Build graphs ────────────────────────────────────────────────────────────
graph = CairoGraph(include_potential=False)
graph_with_potential = CairoGraph(include_potential=True)

# ─── Train ML model on startup ──────────────────────────────────────────────
predictor = get_predictor()
try:
    predictor.train()
    print("[OK] ML Traffic Predictor trained successfully!")
except Exception as e:
    print(f"[WARN] ML model training failed: {e}")

# ─── Page Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─── API Routes ──────────────────────────────────────────────────────────────

@app.route("/api/data")
def get_data():
    """Return all network data for map visualization."""
    return jsonify(graph_with_potential.to_json())


@app.route("/api/mst", methods=["POST"])
def compute_mst():
    """Compute Minimum Spanning Tree."""
    data = request.get_json() or {}
    algorithm = data.get("algorithm", "kruskal")
    prioritize = data.get("prioritize_critical", True)

    g = CairoGraph(include_potential=True)

    if algorithm == "prim":
        result = prim_mst(g, prioritize_critical=prioritize)
    else:
        result = kruskal_mst(g, prioritize_critical=prioritize)

    result["analysis"] = analyze_mst(result)
    return jsonify(result)


@app.route("/api/shortest-path", methods=["POST"])
def compute_shortest_path():
    """Find shortest path using Dijkstra."""
    data = request.get_json() or {}
    source = str(data.get("source", "1"))
    target = str(data.get("target", "3"))
    time_period = data.get("time_period", None)
    k_paths = data.get("k_paths", 1)

    if k_paths > 1:
        routes = yen_k_shortest(graph, source, target, k=k_paths, time_period=time_period)
        return jsonify({
            "algorithm": "Yen's K-Shortest Paths",
            "source": source,
            "target": target,
            "k": k_paths,
            "time_period": time_period or "none",
            "routes": routes,
        })
    else:
        result = dijkstra(graph, source, target, time_period)
        return jsonify(result)


@app.route("/api/emergency-route", methods=["POST"])
def compute_emergency_route():
    """Find emergency route using A*."""
    data = request.get_json() or {}
    source = str(data.get("source", "7"))
    target = data.get("target", None)
    if target:
        target = str(target)
    time_period = data.get("time_period", None)

    result = astar_search(graph, source, target, time_period, emergency_mode=True)

    # Also compute signal preemption for the path
    if result["path"]:
        preemption = emergency_preemption(result["path"])
        result["preemption"] = preemption

    return jsonify(result)


@app.route("/api/transit-optimize", methods=["POST"])
def compute_transit():
    """Optimize transit schedule using DP."""
    data = request.get_json() or {}
    extra_vehicles = data.get("extra_vehicles", 30)
    budget = data.get("budget", 500)

    schedule = optimize_transit_schedule(total_extra_vehicles=extra_vehicles)
    maintenance = road_maintenance_allocation(budget_million_egp=budget)

    return jsonify({
        "schedule_optimization": schedule,
        "road_maintenance": maintenance,
        "cache_stats": get_cache_stats(),
    })


@app.route("/api/signal-optimize", methods=["POST"])
def compute_signals():
    """Optimize traffic signals using greedy."""
    data = request.get_json() or {}
    time_period = data.get("time_period", "morning")
    cycle_length = data.get("cycle_length", 120)

    result = optimize_signals(time_period, cycle_length)
    result["optimality_analysis"] = analyze_greedy_optimality()
    return jsonify(result)


@app.route("/api/traffic-predict", methods=["POST"])
def predict_traffic():
    """ML traffic prediction."""
    data = request.get_json() or {}
    road = data.get("road", None)
    time_period = data.get("time_period", "morning")
    day = data.get("day_of_week", 0)

    if road:
        result = predictor.predict(road, time_period, day)
    else:
        result = predictor.predict_all_roads(time_period, day)

    return jsonify(result)


@app.route("/api/race", methods=["POST"])
def algorithm_race():
    """Dijkstra vs A* race comparison."""
    data = request.get_json() or {}
    source = str(data.get("source", "7"))
    target = str(data.get("target", "F9"))
    time_period = data.get("time_period", None)

    result = compare_dijkstra_vs_astar(graph, source, target, time_period)
    return jsonify(result)


@app.route("/api/simulate", methods=["POST"])
def run_simulation():
    """Run traffic simulation."""
    data = request.get_json() or {}
    scenario = data.get("scenario", "normal")

    result = simulate_traffic(scenario)
    return jsonify(result)


@app.route("/api/alternate-routes", methods=["POST"])
def alternate_routes():
    """Find alternate routes during congestion."""
    data = request.get_json() or {}
    source = str(data.get("source", "1"))
    target = str(data.get("target", "3"))
    time_period = data.get("time_period", "morning")

    result = compare_with_alternate_routes(graph, source, target, time_period)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
