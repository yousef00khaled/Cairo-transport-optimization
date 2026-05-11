"""
Minimum Spanning Tree Algorithms for Infrastructure Network Design.
Implements Kruskal's and Prim's algorithms with priority constraints
for critical facilities (hospitals, government centers).
"""
import heapq
from core.graph import CairoGraph
from data.cairo_data import CRITICAL_FACILITIES, ALL_NODES


# ─── Union-Find (Disjoint Set) for Kruskal's ────────────────────────────────
class UnionFind:
    """Union-Find with path compression and union by rank."""

    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # Union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def kruskal_mst(graph, prioritize_critical=True):
    """
    Kruskal's Algorithm for Minimum Spanning Tree.

    Args:
        graph: CairoGraph instance (should include potential roads)
        prioritize_critical: If True, edges connecting to critical facilities
                           get a priority discount.

    Returns:
        dict with mst_edges, total_distance, total_cost, steps
    """
    nodes = graph.get_all_nodes()
    uf = UnionFind(nodes)
    steps = []

    # Build edge list with modified weights
    edge_list = []
    for u, v, data in graph.edges:
        weight = data["distance"]

        # Priority: discount edges connecting critical facilities
        if prioritize_critical:
            u_is_critical = u in CRITICAL_FACILITIES
            v_is_critical = v in CRITICAL_FACILITIES
            # Also prioritize high-population areas
            u_pop = ALL_NODES.get(u, {}).get("population", 0)
            v_pop = ALL_NODES.get(v, {}).get("population", 0)
            pop_factor = max(u_pop, v_pop) / 550000  # Normalize by max population

            if u_is_critical or v_is_critical:
                weight *= 0.5  # 50% discount for critical facility edges
            elif pop_factor > 0.5:
                weight *= (1.0 - pop_factor * 0.3)  # Up to 30% discount for high-pop

        edge_list.append((weight, u, v, data))

    # Sort edges by weight
    edge_list.sort(key=lambda x: x[0])

    mst_edges = []
    total_distance = 0
    total_cost = 0

    for weight, u, v, data in edge_list:
        if uf.union(u, v):
            mst_edges.append({
                "from": u,
                "to": v,
                "distance": data["distance"],
                "capacity": data["capacity"],
                "is_existing": data["is_existing"],
                "construction_cost": data["construction_cost"],
                "weight_used": round(weight, 2),
            })
            total_distance += data["distance"]
            total_cost += data["construction_cost"]

            steps.append({
                "action": "add_edge",
                "from": u,
                "to": v,
                "distance": data["distance"],
                "total_so_far": round(total_distance, 2),
            })

            if len(mst_edges) == len(nodes) - 1:
                break

    # Check connectivity
    root = uf.find(nodes[0])
    connected = all(uf.find(n) == root for n in nodes)

    return {
        "algorithm": "Kruskal's",
        "mst_edges": mst_edges,
        "total_distance": round(total_distance, 2),
        "total_construction_cost": total_cost,
        "num_edges": len(mst_edges),
        "num_new_roads": sum(1 for e in mst_edges if not e["is_existing"]),
        "fully_connected": connected,
        "steps": steps,
    }


def prim_mst(graph, start_node="3", prioritize_critical=True):
    """
    Prim's Algorithm for Minimum Spanning Tree.

    Args:
        graph: CairoGraph instance
        start_node: Starting node ID (default: Downtown Cairo)
        prioritize_critical: Priority discount for critical facilities

    Returns:
        dict with mst_edges, total_distance, total_cost, steps
    """
    visited = set()
    mst_edges = []
    total_distance = 0
    total_cost = 0
    steps = []

    # Min-heap: (weight, from_node, to_node, edge_data)
    heap = []
    visited.add(start_node)

    # Add edges from start node
    for neighbor, data in graph.get_neighbors(start_node).items():
        weight = data["distance"]
        if prioritize_critical:
            if neighbor in CRITICAL_FACILITIES:
                weight *= 0.5
            else:
                pop = ALL_NODES.get(neighbor, {}).get("population", 0)
                if pop > 275000:
                    weight *= 0.7
        heapq.heappush(heap, (weight, start_node, neighbor, data))

    while heap and len(visited) < len(graph.nodes):
        weight, u, v, data = heapq.heappop(heap)

        if v in visited:
            continue

        visited.add(v)
        mst_edges.append({
            "from": u,
            "to": v,
            "distance": data["distance"],
            "capacity": data["capacity"],
            "is_existing": data["is_existing"],
            "construction_cost": data["construction_cost"],
            "weight_used": round(weight, 2),
        })
        total_distance += data["distance"]
        total_cost += data["construction_cost"]

        steps.append({
            "action": "add_edge",
            "from": u,
            "to": v,
            "distance": data["distance"],
            "total_so_far": round(total_distance, 2),
        })

        # Add edges from newly added node
        for neighbor, ndata in graph.get_neighbors(v).items():
            if neighbor not in visited:
                w = ndata["distance"]
                if prioritize_critical:
                    if neighbor in CRITICAL_FACILITIES:
                        w *= 0.5
                    else:
                        pop = ALL_NODES.get(neighbor, {}).get("population", 0)
                        if pop > 275000:
                            w *= 0.7
                heapq.heappush(heap, (w, v, neighbor, ndata))

    return {
        "algorithm": "Prim's",
        "mst_edges": mst_edges,
        "total_distance": round(total_distance, 2),
        "total_construction_cost": total_cost,
        "num_edges": len(mst_edges),
        "num_new_roads": sum(1 for e in mst_edges if not e["is_existing"]),
        "fully_connected": len(visited) == len(graph.nodes),
        "steps": steps,
    }


def analyze_mst(mst_result):
    """Generate analysis metrics for an MST result."""
    edges = mst_result["mst_edges"]
    existing = [e for e in edges if e["is_existing"]]
    new = [e for e in edges if not e["is_existing"]]

    analysis = {
        "total_edges": len(edges),
        "existing_roads_used": len(existing),
        "new_roads_needed": len(new),
        "total_distance_km": mst_result["total_distance"],
        "total_construction_cost_million_egp": mst_result["total_construction_cost"],
        "avg_distance_per_edge": round(mst_result["total_distance"] / max(len(edges), 1), 2),
        "new_road_details": [{
            "from": e["from"],
            "to": e["to"],
            "distance": e["distance"],
            "cost": e["construction_cost"]
        } for e in new],
    }
    return analysis
