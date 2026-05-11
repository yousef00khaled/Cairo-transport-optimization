"""
Shortest Path Algorithms for Traffic Flow Optimization.
Implements Dijkstra's algorithm with time-dependent traffic support
and k-shortest paths via Yen's algorithm.
"""
import heapq
from copy import deepcopy


def dijkstra(graph, source, target, time_period=None):
    """
    Dijkstra's Algorithm for shortest path.

    Args:
        graph: CairoGraph instance
        source: Source node ID
        target: Target node ID
        time_period: Optional time period for traffic-aware routing
                    ("morning", "afternoon", "evening", "night")

    Returns:
        dict with path, distance, nodes_explored, steps

    Time Complexity: O((V + E) log V) with binary heap
    Space Complexity: O(V)
    """
    dist = {node: float('inf') for node in graph.get_all_nodes()}
    prev = {node: None for node in graph.get_all_nodes()}
    dist[source] = 0
    visited = set()
    steps = []
    nodes_explored = 0

    # Min-heap: (distance, node_id)
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)

        if u in visited:
            continue

        visited.add(u)
        nodes_explored += 1

        steps.append({
            "action": "visit",
            "node": u,
            "distance": round(d, 2),
            "nodes_explored": nodes_explored,
        })

        if u == target:
            break

        for neighbor, edge_data in graph.get_neighbors(u).items():
            if neighbor in visited:
                continue

            weight = graph.get_weight(u, neighbor, time_period)
            new_dist = d + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = u
                heapq.heappush(heap, (new_dist, neighbor))

                steps.append({
                    "action": "relax",
                    "from": u,
                    "to": neighbor,
                    "new_distance": round(new_dist, 2),
                })

    # Reconstruct path
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()

    if dist[target] == float('inf'):
        path = []

    return {
        "algorithm": "Dijkstra",
        "source": source,
        "target": target,
        "path": path,
        "distance": round(dist[target], 2) if dist[target] != float('inf') else None,
        "nodes_explored": nodes_explored,
        "time_period": time_period or "none",
        "steps": steps,
    }


def dijkstra_all(graph, source, time_period=None):
    """
    Dijkstra's Algorithm from source to ALL other nodes.
    Used for memoization and caching sub-problems.

    Returns:
        (dist_dict, prev_dict)
    """
    dist = {node: float('inf') for node in graph.get_all_nodes()}
    prev = {node: None for node in graph.get_all_nodes()}
    dist[source] = 0
    visited = set()
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)

        for neighbor in graph.get_neighbors(u):
            if neighbor in visited:
                continue
            weight = graph.get_weight(u, neighbor, time_period)
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = u
                heapq.heappush(heap, (new_dist, neighbor))

    return dist, prev


def reconstruct_path(prev, target):
    """Reconstruct path from prev dict."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    return path


def yen_k_shortest(graph, source, target, k=3, time_period=None):
    """
    Yen's K-Shortest Paths Algorithm.
    Finds k alternative routes between source and target.

    Args:
        graph: CairoGraph instance
        source: Source node ID
        target: Target node ID
        k: Number of paths to find
        time_period: Optional time period

    Returns:
        list of k paths with distances

    Time Complexity: O(kV(V + E) log V)
    """
    # Find the first shortest path using Dijkstra
    result = dijkstra(graph, source, target, time_period)
    if not result["path"]:
        return []

    A = [{"path": result["path"], "distance": result["distance"]}]
    B = []  # Candidate paths

    for i in range(1, k):
        for j in range(len(A[i - 1]["path"]) - 1):
            spur_node = A[i - 1]["path"][j]
            root_path = A[i - 1]["path"][:j + 1]

            # Track removed edges to restore later
            removed_edges = []

            # Remove edges that are part of previous shortest paths
            for prev_path_data in A:
                prev_path = prev_path_data["path"]
                if len(prev_path) > j and prev_path[:j + 1] == root_path:
                    u = prev_path[j]
                    v = prev_path[j + 1]
                    edge = graph.get_edge(u, v)
                    if edge:
                        removed_edges.append((u, v, deepcopy(edge)))
                        del graph.adj[u][v]
                        if v in graph.adj and u in graph.adj[v]:
                            del graph.adj[v][u]

            # Find spur path
            spur_result = dijkstra(graph, spur_node, target, time_period)

            # Restore removed edges
            for u, v, data in removed_edges:
                graph.adj[u][v] = data
                graph.adj[v][u] = data

            if spur_result["path"]:
                total_path = root_path[:-1] + spur_result["path"]
                # Calculate total distance
                total_dist = 0
                for idx in range(len(total_path) - 1):
                    total_dist += graph.get_weight(total_path[idx], total_path[idx + 1], time_period)

                candidate = {"path": total_path, "distance": round(total_dist, 2)}

                # Check if this path is already in B
                is_dup = False
                for b in B:
                    if b["path"] == candidate["path"]:
                        is_dup = True
                        break
                if not is_dup:
                    B.append(candidate)

        if not B:
            break

        B.sort(key=lambda x: x["distance"])
        A.append(B.pop(0))

    return A
