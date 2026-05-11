"""
Greedy Algorithm for Traffic Signal Optimization.
1. Signal timing optimization at major intersections
2. Emergency vehicle preemption with priority queue
3. Analysis of optimal vs suboptimal greedy decisions
"""
import heapq
from data.cairo_data import (
    TRAFFIC_FLOW, EXISTING_ROADS, ALL_NODES,
    TIME_PERIOD_INDEX, TIME_PERIODS
)


def optimize_signals(time_period="morning", cycle_length=120):
    """
    Greedy Signal Timing Optimization.

    For each intersection, allocates green-light time proportional
    to the traffic flow on each incoming road. This is a greedy
    approach: always give more time to the road with more traffic.

    Args:
        time_period: Time period for traffic data
        cycle_length: Total signal cycle length in seconds

    Returns:
        dict with signal_timings, throughput_improvement

    Time Complexity: O(V * E) where V=intersections, E=edges per intersection
    Space Complexity: O(V * E)
    """
    idx = TIME_PERIOD_INDEX.get(time_period, 0)

    # Find intersections (nodes with degree >= 2)
    # Build adjacency from existing roads
    adj = {}
    for frm, to, dist, cap, cond in EXISTING_ROADS:
        adj.setdefault(frm, []).append(to)
        adj.setdefault(to, []).append(frm)

    intersections = {}
    for node, neighbors in adj.items():
        if len(neighbors) >= 2:
            # Get traffic flow for each incoming road
            incoming_flows = []
            for nb in neighbors:
                road_key = f"{nb}-{node}"
                road_key_rev = f"{node}-{nb}"
                flow_data = TRAFFIC_FLOW.get(road_key) or TRAFFIC_FLOW.get(road_key_rev)
                flow = flow_data[idx] if flow_data else 1000
                incoming_flows.append({"from": nb, "flow": flow})

            intersections[node] = incoming_flows

    # Greedy: allocate green time proportional to traffic flow
    signal_timings = []
    total_improvement = 0

    for node, flows in intersections.items():
        total_flow = sum(f["flow"] for f in flows)
        min_green = 10  # Minimum green time per phase (seconds)
        available_time = cycle_length - len(flows) * min_green  # Reserve minimum for each

        phases = []
        for f in flows:
            proportion = f["flow"] / max(total_flow, 1)
            green_time = min_green + int(available_time * proportion)
            throughput = min(f["flow"], green_time / cycle_length * f["flow"] * 1.5)
            phases.append({
                "from_road": f["from"],
                "traffic_flow": f["flow"],
                "green_time_seconds": green_time,
                "proportion": round(proportion * 100, 1),
                "estimated_throughput": int(throughput),
            })

        # Calculate improvement vs equal split
        equal_green = cycle_length // len(flows)
        greedy_throughput = sum(p["estimated_throughput"] for p in phases)
        equal_throughput = sum(min(f["flow"], equal_green / cycle_length * f["flow"] * 1.5) for f in flows)
        improvement = greedy_throughput - equal_throughput
        total_improvement += improvement

        node_name = ALL_NODES.get(node, {}).get("name", node)
        signal_timings.append({
            "intersection": node,
            "intersection_name": node_name,
            "num_phases": len(phases),
            "cycle_length": cycle_length,
            "phases": phases,
            "greedy_throughput": int(greedy_throughput),
            "equal_throughput": int(equal_throughput),
            "improvement": int(improvement),
            "improvement_pct": round(improvement / max(equal_throughput, 1) * 100, 1),
        })

    signal_timings.sort(key=lambda x: x["improvement"], reverse=True)

    return {
        "algorithm": "Greedy Signal Optimization",
        "time_period": time_period,
        "cycle_length": cycle_length,
        "intersections_optimized": len(signal_timings),
        "total_throughput_improvement": int(total_improvement),
        "signal_timings": signal_timings,
        "complexity": f"O(V × E) = O({len(intersections)} × avg_degree)",
    }


def emergency_preemption(emergency_path, current_queue=None):
    """
    Greedy Emergency Vehicle Preemption.

    Priority-based system for managing emergency vehicle access at
    intersections during high congestion. Uses a priority queue.

    Args:
        emergency_path: List of node IDs the emergency vehicle traverses
        current_queue: Optional dict of vehicles waiting at each intersection

    Returns:
        dict with preemption_schedule, time_saved

    Time Complexity: O(P log V) where P=path length, V=vehicles at intersection
    Space Complexity: O(V)
    """
    if current_queue is None:
        # Simulate queue based on traffic data
        current_queue = {}
        for road_key, flows in TRAFFIC_FLOW.items():
            parts = road_key.split("-")
            for node in parts:
                if node not in current_queue:
                    current_queue[node] = []
                # Add some vehicles to the queue
                current_queue[node].append({
                    "type": "regular",
                    "priority": 0,
                    "wait_time": flows[0] // 100,  # Rough estimate
                })

    preemption_schedule = []
    total_time_saved = 0

    for i, node in enumerate(emergency_path):
        queue = current_queue.get(node, [])

        # Emergency vehicle gets highest priority
        emergency_entry = {
            "type": "emergency",
            "priority": 100,  # Max priority
            "wait_time": 0,
        }

        # Build priority queue (max-heap using negative priority)
        pq = []
        for idx, vehicle in enumerate(queue):
            heapq.heappush(pq, (-vehicle["priority"], idx, vehicle))
        heapq.heappush(pq, (-100, -1, emergency_entry))

        # Find emergency vehicle position in queue
        original_position = len(queue)
        time_saved = sum(v["wait_time"] for v in queue) / max(len(queue), 1) * 0.5

        preemption_schedule.append({
            "intersection": node,
            "intersection_name": ALL_NODES.get(node, {}).get("name", node),
            "vehicles_in_queue": len(queue),
            "original_wait_position": original_position,
            "preempted_to_position": 0,
            "time_saved_seconds": round(time_saved, 1),
            "signal_override": True,
        })
        total_time_saved += time_saved

    return {
        "algorithm": "Greedy Emergency Preemption",
        "path_length": len(emergency_path),
        "preemption_schedule": preemption_schedule,
        "total_time_saved_seconds": round(total_time_saved, 1),
        "total_time_saved_minutes": round(total_time_saved / 60, 2),
    }


def analyze_greedy_optimality():
    """
    Analyze cases where greedy signal optimization is optimal vs suboptimal.

    Returns analysis comparing greedy to alternative approaches.
    """
    return {
        "optimal_cases": [
            {
                "scenario": "Two-phase intersection with clear traffic imbalance",
                "explanation": "When one road has significantly more traffic, "
                             "greedy proportional allocation is provably optimal "
                             "as it maximizes total throughput.",
                "example": "Downtown Cairo (3) - Zamalek (6) intersection during morning rush",
            },
            {
                "scenario": "Low-traffic night periods",
                "explanation": "During night with low overall traffic, any reasonable "
                             "allocation achieves near-optimal throughput since demand "
                             "is well below capacity.",
                "example": "All intersections during night period (400-800 veh/h)",
            },
        ],
        "suboptimal_cases": [
            {
                "scenario": "Multi-phase intersections with coordinated traffic",
                "explanation": "When adjacent intersections have coordinated signals "
                             "(green wave), local greedy optimization at each intersection "
                             "may break the coordination, leading to worse global throughput.",
                "example": "Mohandessin (9) - Dokki (10) - Downtown (3) corridor",
            },
            {
                "scenario": "Intersections near events or road closures",
                "explanation": "Greedy cannot anticipate sudden traffic changes from "
                             "events at Cairo International Stadium or accidents. "
                             "A predictive approach would outperform greedy.",
                "example": "Roads near F6 (Cairo International Stadium) during match days",
            },
            {
                "scenario": "Circular traffic patterns (Egyptian roundabouts)",
                "explanation": "Cairo's roundabouts create circular dependencies where "
                             "greedy allocation at one entry affects all others. "
                             "A global optimization (LP/DP) would be superior.",
                "example": "Tahrir Square area connecting Downtown, Dokki, and Garden City",
            },
        ],
        "conclusion": "Greedy signal optimization works well for isolated intersections "
                     "with clear traffic imbalance, but complex urban networks like Cairo "
                     "benefit from coordinated optimization approaches."
    }
