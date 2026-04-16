from algorithms.greedy_tsp import greedy_tsp
from algorithms.dp_tsp import dp_tsp
from algorithms.heuristic_tsp import heuristic_tsp

def run_tsp_algorithms(distance_matrix):
    n = len(distance_matrix)

    print(f"Graph size: {n}")

    results = {}

    results["greedy"] = greedy_tsp(distance_matrix)
    results["heuristic"] = heuristic_tsp(distance_matrix)

    if n <= 12:
        results["dp"] = dp_tsp(distance_matrix)
    else:
        results["dp"] = "Skipped (too large)"

    return results