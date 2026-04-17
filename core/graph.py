import osmnx as ox
import json
import random

def create_small_graph():
    graph = {
        0: [(1, 4), (2, 2)],
        1: [(0, 4), (3, 5), (4, 10)],
        2: [(0, 2), (5, 3)],
        3: [(1, 5), (6, 2)],
        4: [(1, 10), (7, 6)],
        5: [(2, 3), (6, 4), (8, 8)],
        6: [(3, 2), (5, 4), (9, 7)],
        7: [(4, 6)],
        8: [(5, 8)],
        9: [(6, 7)]
    }

    coordinates = {i: (0, 0) for i in graph}

    return graph, coordinates

def generate_medium_graph(n=50, edge_prob=0.2):
    graph = {i: [] for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < edge_prob:
                weight = random.randint(1, 20)
                graph[i].append((j, weight))
                graph[j].append((i, weight))

    # ensure connectivity (important)
    for i in range(n - 1):
        if not any(neigh == i + 1 for neigh, _ in graph[i]):
            weight = random.randint(1, 10)
            graph[i].append((i + 1, weight))
            graph[i + 1].append((i, weight))

    coordinates = {i: (random.uniform(0, 10), random.uniform(0, 10)) for i in graph}

    return graph, coordinates

class GraphLoader:
    def __init__(self):
        self.G = None
        self.graph = {}
        self.coordinates = {}

    # -------------------------------
    # STEP 1: Load OSM Data (POINT METHOD)
    # -------------------------------
    def load_osm_graph(self):
        center_point = (12.915, 79.145)  # Vellore
        dist = 3000  # controls size

        print("Using center:", center_point, "radius:", dist)

        self.G = ox.graph_from_point(
            center_point,
            dist=dist,
            network_type='drive'
        )

        print("Raw graph loaded")

    # -------------------------------
    # STEP 2: Simplify Graph
    # -------------------------------
    def preprocess_graph(self):
        try:
            self.G = ox.utils_graph.get_largest_component(self.G, strongly=True)
        except:
            pass  # safe fallback

    print("Graph cleaned (already simplified)")

    # -------------------------------
    # STEP 3: Convert to Adjacency List
    # -------------------------------
    def convert_to_adjacency_list(self):
        for node in self.G.nodes:
            self.graph[node] = []
            self.coordinates[node] = (
                self.G.nodes[node]['x'],
                self.G.nodes[node]['y']
            )

        for u, v, data in self.G.edges(data=True):
            weight = data.get('length', 1)
            self.graph[u].append((v, weight))

        print("Converted to adjacency list")

    # -------------------------------
    # STEP 4: Traffic Simulation
    # -------------------------------
    def apply_traffic(self, factor=0.3):
        for u in self.graph:
            self.graph[u] = [
                (v, w * random.uniform(1, 1 + factor))
                for v, w in self.graph[u]
            ]
        print("Traffic simulation applied")

    # -------------------------------
    # STEP 5: Save Dataset
    # -------------------------------
    def save(self, filename):
        with open(filename, "w") as f:
            json.dump({
                "graph": self.graph,
                "coordinates": self.coordinates
            }, f)
        print(f"Graph saved to {filename}")

    # -------------------------------
    # STEP 6: Load Dataset
    # -------------------------------
    @staticmethod
    def load(filename):
        with open(filename) as f:
            data = json.load(f)
        return data["graph"], data["coordinates"]

    # -------------------------------
    # STEP 7: Stats
    # -------------------------------
    def print_stats(self):
        num_nodes = len(self.graph)
        num_edges = sum(len(v) for v in self.graph.values())

        print(f"Nodes: {num_nodes}")
        print(f"Edges: {num_edges}")