import json
from algorthms.utils import graph_to_distance_matrix
from algorthms.route_optimizer import run_tsp_algorithms

# Load dataset (change file if needed)
with open("datasets/small_graph.json") as f:
    data=json.load(f)

graph=data["graph"]

# Convert graph → distance matrix
from algorithms.dijkstra import get_distance_matrix

distance_matrix = get_distance_matrix(graph)

# Run TSP algorithms
results=run_tsp_algorithms(distance_matrix)
for row in distance_matrix:
    print(row)
# Print results
print("\n--- RESULTS ---")
print("Greedy:", results["greedy"])
print("DP:", results["dp"])