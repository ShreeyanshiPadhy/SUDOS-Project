import osmnx as ox
import heapq
import random

# -------------------------------
# GRAPH CREATION (SMALL)
# -------------------------------
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
    coords = {i: (0, 0) for i in graph}
    return graph, coords


# -------------------------------
# GRAPH CREATION (MEDIUM)
# -------------------------------
def generate_medium_graph(n=50, edge_prob=0.2):
    graph = {i: [] for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < edge_prob:
                w = random.randint(1, 20)
                graph[i].append((j, w))
                graph[j].append((i, w))

    # ensure connectivity
    for i in range(n - 1):
        if not any(neigh == i + 1 for neigh, _ in graph[i]):
            w = random.randint(1, 10)
            graph[i].append((i + 1, w))
            graph[i + 1].append((i, w))

    coords = {i: (random.uniform(0, 10), random.uniform(0, 10)) for i in graph}
    return graph, coords


# -------------------------------
# OSM GRAPH LOADER
# -------------------------------
class GraphLoader:
    def __init__(self):
        self.G = None
        self.graph = {}

    def load_osm_graph(self):
        center = (12.915, 79.145)  # Vellore
        self.G = ox.graph_from_point(center, dist=3000, network_type='drive')

    def preprocess_graph(self):
        try:
            self.G = ox.utils_graph.get_largest_component(self.G, strongly=True)
        except:
            pass

    def convert_to_adjacency_list(self):
        for node in self.G.nodes:
            self.graph[node] = []

        for u, v, data in self.G.edges(data=True):
            w = data.get('length', 1)
            self.graph[u].append((v, w))

    def apply_traffic(self, factor=0.3):
        for u in self.graph:
            self.graph[u] = [
                (v, w * random.uniform(1, 1 + factor))
                for v, w in self.graph[u]
            ]


# -------------------------------
# DIJKSTRA + PATH
# -------------------------------
def dijkstra(graph, source, target):
    dist = {node: float('inf') for node in graph}
    parent = {node: None for node in graph}

    dist[source] = 0
    pq = [(0, source)]

    while pq:
        curr_dist, u = heapq.heappop(pq)

        if curr_dist > dist[u]:
            continue

        for v, w in graph[u]:
            if dist[v] > curr_dist + w:
                dist[v] = curr_dist + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    # reconstruct path
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]

    path.reverse()
    return dist[target], path


# -------------------------------
# MAIN DRIVER
# -------------------------------
if __name__ == "__main__":

    # -------- CHOOSE ONE --------
    # graph, coords = create_small_graph()
    # graph, coords = generate_medium_graph()

    loader = GraphLoader()
    loader.load_osm_graph()
    loader.preprocess_graph()
    loader.convert_to_adjacency_list()
    loader.apply_traffic()
    graph = loader.graph

    # pick random nodes
    nodes = list(graph.keys())
    source = nodes[0]
    target = nodes[50]

    distance, path = dijkstra(graph, source, target)

    print("Source:", source)
    print("Target:", target)
    print("Shortest Distance:", distance)
    print("Path:", path)
import heapq

def single_source_dijkstra(graph, source):
    dist = {node: float('inf') for node in graph}
    dist[source] = 0

    pq = [(0, source)]

    while pq:
        curr_dist, u = heapq.heappop(pq)

        if curr_dist > dist[u]:
            continue

        for v, w in graph[u]:
            if dist[v] > curr_dist + w:
                dist[v] = curr_dist + w
                heapq.heappush(pq, (dist[v], v))

    return dist


def get_distance_matrix(graph):
    nodes = list(graph.keys())
    n = len(nodes)

    node_index = {node: i for i, node in enumerate(nodes)}

    dist_matrix = [[float('inf')] * n for _ in range(n)]

    for src in nodes:
        distances = single_source_dijkstra(graph, src)

        for dest in nodes:
            i = node_index[src]
            j = node_index[dest]
            dist_matrix[i][j] = distances[dest]

    return dist_matrix