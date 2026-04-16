import json
import argparse
import logging
import sys

from algorithms.route_optimizer import run_tsp_algorithms
from algorithms.utils import graph_to_distance_matrix

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Run SUDOS Algorithms")
    parser.add_argument("--dataset", type=str, default="datasets/small_graph.json", help="Path to the dataset JSON file")
    parser.add_argument("--verbose", action="store_true", help="Print distance matrix")
    
    args = parser.parse_args()

    try:
        with open(args.dataset, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Dataset file '{args.dataset}' not found.")
        logging.info("Please generate one using: python tools/generate_datasets.py --size small")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Dataset file '{args.dataset}' is invalid JSON.")
        sys.exit(1)

    graph = data.get("graph")
    if not graph:
        logging.error("Dataset must contain a 'graph' key.")
        sys.exit(1)

    logging.info(f"Loaded dataset: {args.dataset}")
    logging.info("Converting graph to distance matrix...")
    
    distance_matrix = graph_to_distance_matrix(graph)

    if args.verbose:
        logging.info("Distance Matrix Output:")
        for row in distance_matrix:
            print(row)

    logging.info("Running TSP algorithms...")
    results = run_tsp_algorithms(distance_matrix)
    
    print("\n--- PERFORMANCE RESULTS ---")
    print(f"Greedy Cost: {results.get('greedy')}")
    print(f"DP Cost:     {results.get('dp')}")

if __name__ == "__main__":
    main()
