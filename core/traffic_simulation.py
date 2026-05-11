"""
Traffic Simulation Framework.
Simulates traffic across different time periods and scenarios.
"""
from data.cairo_data import (
    TRAFFIC_FLOW, EXISTING_ROADS, TIME_PERIODS,
    TIME_PERIOD_INDEX, ALL_NODES
)
from core.graph import CairoGraph
from core.shortest_path import dijkstra


def simulate_traffic(scenario="normal"):
    """
    Simulate traffic across all time periods.

    Args:
        scenario: "normal", "accident", "event"

    Returns:
        dict with simulation results per time period
    """
    results = {}

    for period in TIME_PERIODS:
        graph = CairoGraph(include_potential=False)
        period_data = _analyze_period(graph, period, scenario)
        results[period] = period_data

    return {
        "scenario": scenario,
        "time_periods": results,
        "summary": _summarize_simulation(results),
    }


def _analyze_period(graph, period, scenario):
    """Analyze traffic for a specific time period."""
    idx = TIME_PERIOD_INDEX[period]

    congested_roads = []
    total_flow = 0
    total_capacity = 0

    for frm, to, dist, cap, cond in EXISTING_ROADS:
        road_key = f"{frm}-{to}"
        road_key_rev = f"{to}-{frm}"
        flow_data = TRAFFIC_FLOW.get(road_key) or TRAFFIC_FLOW.get(road_key_rev)

        if flow_data:
            flow = flow_data[idx]

            # Apply scenario modifiers
            if scenario == "accident" and road_key in ["3-5", "2-3"]:
                flow = int(flow * 1.8)  # Accident increases congestion
                cap_effective = int(cap * 0.3)  # Reduced capacity
            elif scenario == "event" and road_key in ["F1-5", "F1-2", "5-11"]:
                flow = int(flow * 1.5)  # Event increases traffic
                cap_effective = cap
            else:
                cap_effective = cap

            congestion_ratio = flow / max(cap_effective, 1)
            total_flow += flow
            total_capacity += cap_effective

            if congestion_ratio > 0.8:
                congested_roads.append({
                    "road": road_key,
                    "from_name": ALL_NODES.get(frm, {}).get("name", frm),
                    "to_name": ALL_NODES.get(to, {}).get("name", to),
                    "flow": flow,
                    "capacity": cap_effective,
                    "congestion_ratio": round(congestion_ratio, 2),
                    "status": "severe" if congestion_ratio > 1.0 else "moderate",
                })

    congested_roads.sort(key=lambda x: x["congestion_ratio"], reverse=True)

    # Sample route analysis
    sample_routes = []
    test_pairs = [("1", "3"), ("7", "3"), ("4", "3"), ("12", "5")]
    for src, tgt in test_pairs:
        result = dijkstra(graph, src, tgt, period)
        if result["path"]:
            sample_routes.append({
                "from": src,
                "to": tgt,
                "from_name": ALL_NODES.get(src, {}).get("name", src),
                "to_name": ALL_NODES.get(tgt, {}).get("name", tgt),
                "distance": result["distance"],
                "hops": len(result["path"]) - 1,
            })

    return {
        "period": period,
        "total_flow": total_flow,
        "total_capacity": total_capacity,
        "overall_congestion": round(total_flow / max(total_capacity, 1), 2),
        "congested_roads": congested_roads,
        "num_congested": len(congested_roads),
        "sample_routes": sample_routes,
    }


def _summarize_simulation(results):
    """Summarize simulation results."""
    worst_period = max(results.keys(), key=lambda p: results[p]["overall_congestion"])
    best_period = min(results.keys(), key=lambda p: results[p]["overall_congestion"])

    return {
        "worst_period": worst_period,
        "worst_congestion": results[worst_period]["overall_congestion"],
        "best_period": best_period,
        "best_congestion": results[best_period]["overall_congestion"],
        "most_congested_roads": results[worst_period]["congested_roads"][:5],
    }


def compare_with_alternate_routes(graph, source, target, time_period="morning"):
    """
    Compare original route with alternate routes during congestion.
    Demonstrates route recommendation during road closures.
    """
    from core.shortest_path import yen_k_shortest

    routes = yen_k_shortest(graph, source, target, k=3, time_period=time_period)

    return {
        "source": source,
        "target": target,
        "source_name": ALL_NODES.get(source, {}).get("name", source),
        "target_name": ALL_NODES.get(target, {}).get("name", target),
        "time_period": time_period,
        "routes": routes,
        "recommendation": routes[0] if routes else None,
    }
