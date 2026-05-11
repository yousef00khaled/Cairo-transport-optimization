"""
Graph Data Structure for Cairo Transportation Network.
Weighted undirected graph with temporal traffic support.
"""
import math
import sys
sys.path.insert(0, '.')
from data.cairo_data import (
    ALL_NODES, EXISTING_ROADS, POTENTIAL_ROADS,
    TRAFFIC_FLOW, TIME_PERIOD_INDEX
)


class CairoGraph:
    """Weighted undirected graph representing Cairo's road network."""

    def __init__(self, include_potential=False):
        """
        Build the graph from project data.
        Args:
            include_potential: If True, also include potential new roads.
        """
        self.adj = {}          # node_id -> {neighbor_id: edge_data}
        self.nodes = {}        # node_id -> node_data
        self.edges = []        # list of all edges for MST algorithms

        # Add all nodes
        for nid, data in ALL_NODES.items():
            self.add_node(nid, data)

        # Add existing roads
        for frm, to, dist, cap, cond in EXISTING_ROADS:
            self.add_edge(frm, to, dist, cap, cond, is_existing=True, cost=0)

        # Optionally add potential roads
        if include_potential:
            for frm, to, dist, cap, cost in POTENTIAL_ROADS:
                self.add_edge(frm, to, dist, cap, 10, is_existing=False, cost=cost)

    def add_node(self, node_id, data):
        """Add a node with its metadata."""
        self.nodes[node_id] = data
        if node_id not in self.adj:
            self.adj[node_id] = {}

    def add_edge(self, u, v, distance, capacity, condition, is_existing=True, cost=0):
        """Add an undirected edge between u and v."""
        edge_data = {
            "distance": distance,
            "capacity": capacity,
            "condition": condition,
            "is_existing": is_existing,
            "construction_cost": cost,
        }
        # Ensure both nodes exist in adjacency
        if u not in self.adj:
            self.adj[u] = {}
        if v not in self.adj:
            self.adj[v] = {}

        self.adj[u][v] = edge_data
        self.adj[v][u] = edge_data
        self.edges.append((u, v, edge_data))

    def get_neighbors(self, node_id):
        """Return neighbors of a node as dict {neighbor: edge_data}."""
        return self.adj.get(node_id, {})

    def get_edge(self, u, v):
        """Get edge data between u and v."""
        return self.adj.get(u, {}).get(v, None)

    def get_all_nodes(self):
        """Return all node IDs."""
        return list(self.nodes.keys())

    def get_node_coords(self, node_id):
        """Return (lon, lat) for a node."""
        n = self.nodes.get(node_id)
        if n:
            return (n["x"], n["y"])
        return None

    def get_weight(self, u, v, time_period=None):
        """
        Get edge weight, optionally adjusted for time-of-day traffic.
        Weight = distance * congestion_factor
        congestion_factor = traffic_flow / capacity (capped at 2.0)
        """
        edge = self.get_edge(u, v)
        if not edge:
            return float('inf')

        base_distance = edge["distance"]

        if time_period is None:
            return base_distance

        # Look up traffic flow for this edge
        road_key = f"{u}-{v}"
        road_key_rev = f"{v}-{u}"
        flow_data = TRAFFIC_FLOW.get(road_key) or TRAFFIC_FLOW.get(road_key_rev)

        if flow_data:
            idx = TIME_PERIOD_INDEX.get(time_period, 0)
            current_flow = flow_data[idx]
            capacity = edge["capacity"]
            # Congestion factor: ratio of flow to capacity
            congestion = min(current_flow / capacity, 2.0) if capacity > 0 else 1.0
            # Apply congestion multiplier (1.0 = free flow, 2.0 = severe congestion)
            return base_distance * (0.5 + congestion)
        else:
            return base_distance

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """Calculate Haversine distance in km between two GPS points."""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def heuristic(self, node_id, goal_id):
        """A* heuristic: Haversine distance between two nodes, scaled for admissibility.
        
        The raw Haversine (great-circle) distance can exceed the road distances
        in our dataset (which are manually assigned, not actual GPS-measured routes).
        We scale by 0.55 to guarantee the heuristic never overestimates, keeping
        A* optimal while still providing meaningful guidance.
        """
        c1 = self.get_node_coords(node_id)
        c2 = self.get_node_coords(goal_id)
        if c1 and c2:
            return self.haversine(c1[0], c1[1], c2[0], c2[1]) * 0.55
        return 0

    def to_json(self):
        """Serialize graph data for the frontend."""
        nodes_json = []
        for nid, data in self.nodes.items():
            nodes_json.append({
                "id": nid,
                "name": data.get("name", nid),
                "population": data.get("population", 0),
                "type": data.get("type", "Unknown"),
                "x": data["x"],
                "y": data["y"],
            })

        edges_json = []
        seen = set()
        for u, v, data in self.edges:
            key = tuple(sorted([u, v]))
            if key not in seen:
                seen.add(key)
                # Get traffic data
                road_key = f"{u}-{v}"
                road_key_rev = f"{v}-{u}"
                flow = TRAFFIC_FLOW.get(road_key) or TRAFFIC_FLOW.get(road_key_rev)
                edges_json.append({
                    "from": u,
                    "to": v,
                    "distance": data["distance"],
                    "capacity": data["capacity"],
                    "condition": data["condition"],
                    "is_existing": data["is_existing"],
                    "construction_cost": data["construction_cost"],
                    "traffic_flow": list(flow) if flow else None,
                })

        return {"nodes": nodes_json, "edges": edges_json}
