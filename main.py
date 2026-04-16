import json
import argparse
import logging
import sys

from algorithms.route_optimizer import run_tsp_algorithms

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Run SUDOS Algorithms")
    parser.add_argument("--dataset", type=str, default="datasets/small_graph.json")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    # Load dataset
    try:
        with open(args.dataset, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Dataset file '{args.dataset}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in dataset.")
        sys.exit(1)

    graph = data.get("graph")
    if not graph:
        logging.error("Dataset must contain a 'graph' key.")
        sys.exit(1)

    # Convert to int
    graph = {
        int(node): [(int(neigh), weight) for neigh, weight in edges]
        for node, edges in graph.items()
    }

    # 🔥 FIX 3: Ensure connected subgraph using BFS
    MAX_NODES = 50

    start = list(graph.keys())[0]
    visited = set([start])
    queue = [start]

    while queue and len(visited) < MAX_NODES:
        node = queue.pop(0)
        for neigh, _ in graph[node]:
            if neigh not in visited:
                visited.add(neigh)
                queue.append(neigh)

    selected_nodes = visited

    # Filter graph properly
    graph = {
        node: [(neigh, w) for neigh, w in graph[node] if neigh in selected_nodes]
        for node in selected_nodes
    }
    logging.info(f"Loaded dataset: {args.dataset}")

    # 🔥 USE DIJKSTRA (IMPORTANT)
    logging.info("Running Dijkstra (all-pairs shortest paths)...")
    from algorithms.dijkstra import get_distance_matrix
    distance_matrix = get_distance_matrix(graph)

    if args.verbose:
        logging.info("Distance Matrix:")
        for row in distance_matrix:
            print(row)

    logging.info("Running TSP algorithms...")
    results = run_tsp_algorithms(distance_matrix)

    print("\n--- PERFORMANCE RESULTS ---")

    # Always print greedy
    print(f"Greedy:    {results.get('greedy')}")

    # Print heuristic if exists
    if "heuristic" in results:
        print(f"Heuristic: {results.get('heuristic')}")

    # Print DP if exists
    print(f"DP:        {results.get('dp')}")

if __name__ == "__main__":
    main()