"""
A* Search Algorithm for Emergency Response Planning.
Routes emergency vehicles to the nearest medical facility
using Haversine distance as heuristic.
"""
import heapq
from data.cairo_data import MEDICAL_FACILITIES


def astar_search(graph, source, target=None, time_period=None, emergency_mode=True):
    """
    A* Search Algorithm for emergency vehicle routing.

    If target is None, routes to the nearest medical facility.
    Uses Haversine distance as the admissible heuristic.

    Args:
        graph: CairoGraph instance
        source: Source node ID (emergency origin)
        target: Target node ID (if None, finds nearest hospital)
        time_period: Time period for traffic-aware routing
        emergency_mode: If True, reduces congestion weights (signal preemption)

    Returns:
        dict with path, distance, nodes_explored, steps, target

    Time Complexity: O((V + E) log V) - same as Dijkstra but explores fewer nodes
    Space Complexity: O(V)
    """
    # If no target specified, find nearest medical facility
    if target is None:
        targets = MEDICAL_FACILITIES
    else:
        targets = [target]

    best_result = None

    for goal in targets:
        result = _astar_to_goal(graph, source, goal, time_period, emergency_mode)
        if result["path"] and (best_result is None or result["distance"] < best_result["distance"]):
            best_result = result

    if best_result is None:
        return {
            "algorithm": "A*",
            "source": source,
            "target": None,
            "path": [],
            "distance": None,
            "nodes_explored": 0,
            "time_period": time_period or "none",
            "emergency_mode": emergency_mode,
            "steps": [],
        }

    return best_result


def _astar_to_goal(graph, source, goal, time_period, emergency_mode):
    """A* search to a specific goal node."""
    g_score = {node: float('inf') for node in graph.get_all_nodes()}
    f_score = {node: float('inf') for node in graph.get_all_nodes()}
    prev = {node: None for node in graph.get_all_nodes()}

    g_score[source] = 0
    f_score[source] = graph.heuristic(source, goal)

    visited = set()
    steps = []
    nodes_explored = 0

    # Min-heap: (f_score, g_score, node_id)
    # g_score as tiebreaker for equal f_scores
    heap = [(f_score[source], 0, source)]
    counter = 0  # Unique counter for heap stability

    while heap:
        f, g, u = heapq.heappop(heap)

        if u in visited:
            continue

        visited.add(u)
        nodes_explored += 1

        steps.append({
            "action": "visit",
            "node": u,
            "g_score": round(g_score[u], 2),
            "f_score": round(f, 2),
            "heuristic": round(f - g_score[u], 2),
            "nodes_explored": nodes_explored,
        })

        if u == goal:
            break

        for neighbor, edge_data in graph.get_neighbors(u).items():
            if neighbor in visited:
                continue

            # Calculate weight
            weight = graph.get_weight(u, neighbor, time_period)

            # Emergency mode: signal preemption reduces effective congestion
            if emergency_mode:
                weight *= 0.6  # 40% reduction due to priority signals & sirens

            tentative_g = g_score[u] + weight

            if tentative_g < g_score[neighbor]:
                prev[neighbor] = u
                g_score[neighbor] = tentative_g
                h = graph.heuristic(neighbor, goal)
                f_score[neighbor] = tentative_g + h
                counter += 1
                heapq.heappush(heap, (f_score[neighbor], counter, neighbor))

                steps.append({
                    "action": "relax",
                    "from": u,
                    "to": neighbor,
                    "g_score": round(tentative_g, 2),
                    "f_score": round(f_score[neighbor], 2),
                })

    # Reconstruct path
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()

    if g_score[goal] == float('inf'):
        path = []

    return {
        "algorithm": "A*",
        "source": source,
        "target": goal,
        "target_name": graph.nodes.get(goal, {}).get("name", goal),
        "path": path,
        "distance": round(g_score[goal], 2) if g_score[goal] != float('inf') else None,
        "nodes_explored": nodes_explored,
        "time_period": time_period or "none",
        "emergency_mode": emergency_mode,
        "steps": steps,
    }


def compare_dijkstra_vs_astar(graph, source, target, time_period=None):
    """
    Race comparison between Dijkstra and A* for the bonus visualizer.

    Returns:
        dict with both results and comparison metrics
    """
    from core.shortest_path import dijkstra

    dijkstra_result = dijkstra(graph, source, target, time_period)
    astar_result = astar_search(graph, source, target, time_period, emergency_mode=False)

    return {
        "dijkstra": dijkstra_result,
        "astar": astar_result,
        "comparison": {
            "dijkstra_nodes_explored": dijkstra_result["nodes_explored"],
            "astar_nodes_explored": astar_result["nodes_explored"],
            "nodes_saved": dijkstra_result["nodes_explored"] - astar_result["nodes_explored"],
            "efficiency_gain_pct": round(
                (1 - astar_result["nodes_explored"] / max(dijkstra_result["nodes_explored"], 1)) * 100, 1
            ),
            "same_distance": dijkstra_result["distance"] == astar_result["distance"],
            "dijkstra_path_length": len(dijkstra_result["path"]),
            "astar_path_length": len(astar_result["path"]),
        }
    }
