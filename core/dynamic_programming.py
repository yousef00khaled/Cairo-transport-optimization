"""
Dynamic Programming Solutions for Public Transit Optimization.
1. Bus/Metro Schedule Optimization (minimize passenger wait time)
2. Road Maintenance Resource Allocation (0/1 Knapsack)
3. Route Planning Memoization
"""
from data.cairo_data import (
    METRO_LINES, BUS_ROUTES, TRANSIT_DEMAND,
    EXISTING_ROADS, TRAFFIC_FLOW, TIME_PERIODS
)


def optimize_transit_schedule(total_extra_vehicles=30, time_slots=4):
    """
    DP Solution: Optimal allocation of extra vehicles across transit lines.

    Minimizes total weighted passenger wait time by distributing
    extra vehicles to the lines that benefit most.

    State: dp[i][j] = min total wait if we've considered first i lines
                      and allocated j extra vehicles total
    Decision: how many extra vehicles to give line i (0..j)

    Args:
        total_extra_vehicles: Total extra buses/trains to distribute
        time_slots: Number of time periods per day

    Returns:
        dict with allocation, total_improvement, steps

    Time Complexity: O(L * V^2) where L=lines, V=vehicles
    Space Complexity: O(L * V)
    """
    # Combine all transit lines
    lines = []
    for lid, data in METRO_LINES.items():
        lines.append({
            "id": lid,
            "name": data["name"],
            "type": "metro",
            "daily_passengers": data["daily_passengers"],
            "current_vehicles": 10,  # Assumed base for metro
            "stations": len(data["stations"]),
        })
    for lid, data in BUS_ROUTES.items():
        lines.append({
            "id": lid,
            "name": f"Bus {lid}",
            "type": "bus",
            "daily_passengers": data["daily_passengers"],
            "current_vehicles": data["buses"],
            "stations": len(data["stops"]),
        })

    n_lines = len(lines)
    V = total_extra_vehicles

    # dp[i][j] = min total wait time considering lines 0..i-1, j vehicles allocated
    INF = float('inf')
    dp = [[INF] * (V + 1) for _ in range(n_lines + 1)]
    choice = [[0] * (V + 1) for _ in range(n_lines + 1)]
    dp[0][0] = 0

    def wait_time(line, extra):
        """Estimate average wait time reduction with extra vehicles."""
        total_vehicles = line["current_vehicles"] + extra
        # Average headway = operating_hours / (vehicles * trips_per_vehicle)
        # More vehicles → shorter headway → less wait
        base_wait = 60 / max(line["current_vehicles"], 1)  # minutes
        new_wait = 60 / max(total_vehicles, 1)
        # Weighted by passengers
        reduction = (base_wait - new_wait) * line["daily_passengers"]
        return -reduction  # Negative because we minimize (more reduction = better)

    for i in range(1, n_lines + 1):
        line = lines[i - 1]
        for j in range(V + 1):
            for alloc in range(j + 1):
                prev = dp[i - 1][j - alloc]
                if prev == INF:
                    continue
                cost = prev + wait_time(line, alloc)
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    choice[i][j] = alloc

    # Find best total allocation
    best_j = min(range(V + 1), key=lambda j: dp[n_lines][j])

    # Backtrack to find allocation per line
    allocation = []
    remaining = best_j
    for i in range(n_lines, 0, -1):
        alloc = choice[i][remaining]
        line = lines[i - 1]
        allocation.append({
            "line_id": line["id"],
            "line_name": line["name"],
            "type": line["type"],
            "current_vehicles": line["current_vehicles"],
            "extra_allocated": alloc,
            "total_vehicles": line["current_vehicles"] + alloc,
            "daily_passengers": line["daily_passengers"],
            "wait_reduction_pct": round(alloc / max(line["current_vehicles"], 1) * 100, 1),
        })
        remaining -= alloc

    allocation.reverse()

    return {
        "algorithm": "Dynamic Programming - Transit Schedule Optimization",
        "total_extra_vehicles": V,
        "vehicles_used": best_j,
        "allocation": allocation,
        "lines_improved": sum(1 for a in allocation if a["extra_allocated"] > 0),
        "complexity": f"O(L × V²) = O({n_lines} × {V}²)",
    }


def road_maintenance_allocation(budget_million_egp=500):
    """
    DP Solution: 0/1 Knapsack for Road Maintenance Resource Allocation.

    Each road segment is an "item" with:
    - Weight = maintenance cost (proportional to distance / condition)
    - Value = improvement potential (worse condition = higher value)

    Args:
        budget_million_egp: Total maintenance budget in million EGP

    Returns:
        dict with selected_roads, total_cost, total_improvement

    Time Complexity: O(n * W) where n=roads, W=budget
    Space Complexity: O(n * W)
    """
    # Build items from existing roads
    items = []
    for frm, to, dist, cap, cond in EXISTING_ROADS:
        # Cost proportional to distance, inversely to condition
        cost = int(dist * (11 - cond) * 2)  # In million EGP units
        # Value: improvement potential (worse roads = more value)
        value = int((11 - cond) * dist * cap / 1000)
        items.append({
            "from": frm,
            "to": to,
            "distance": dist,
            "condition": cond,
            "cost": cost,
            "value": value,
        })

    n = len(items)
    W = budget_million_egp

    # DP table
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]  # Don't take item i
            if items[i - 1]["cost"] <= w:
                val = dp[i - 1][w - items[i - 1]["cost"]] + items[i - 1]["value"]
                if val > dp[i][w]:
                    dp[i][w] = val

    # Backtrack to find selected items
    selected = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(items[i - 1])
            w -= items[i - 1]["cost"]

    selected.reverse()
    total_cost = sum(s["cost"] for s in selected)
    total_value = sum(s["value"] for s in selected)

    return {
        "algorithm": "Dynamic Programming - 0/1 Knapsack Road Maintenance",
        "budget": budget_million_egp,
        "total_roads_considered": n,
        "roads_selected": len(selected),
        "total_cost": total_cost,
        "total_improvement_value": total_value,
        "budget_utilization_pct": round(total_cost / max(budget_million_egp, 1) * 100, 1),
        "selected_roads": [{
            "from": s["from"],
            "to": s["to"],
            "distance": s["distance"],
            "current_condition": s["condition"],
            "maintenance_cost": s["cost"],
            "improvement_value": s["value"],
        } for s in selected],
        "complexity": f"O(n × W) = O({n} × {budget_million_egp})",
    }


# ─── Route Memoization Cache ────────────────────────────────────────────────
_route_cache = {}


def memoized_route(graph, source, target, time_period=None):
    """
    Memoized route planning - caches computed shortest paths.

    Time Complexity: O(1) for cache hit, O((V+E)logV) for cache miss
    """
    from core.shortest_path import dijkstra

    key = (source, target, time_period)
    if key not in _route_cache:
        _route_cache[key] = dijkstra(graph, source, target, time_period)
    return _route_cache[key]


def clear_route_cache():
    """Clear the memoization cache."""
    global _route_cache
    _route_cache = {}


def get_cache_stats():
    """Return memoization cache statistics."""
    return {
        "cached_routes": len(_route_cache),
        "cache_keys": [f"{k[0]}→{k[1]} ({k[2] or 'any'})" for k in _route_cache],
    }
