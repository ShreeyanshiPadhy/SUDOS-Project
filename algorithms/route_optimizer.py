import time
from algorithms.greedy_tsp import greedy_tsp
from algorithms.dp_tsp import dp_tsp
from algorithms.heuristic_tsp import heuristic_tsp

def run_tsp_algorithms(distance_matrix):
    n = len(distance_matrix)
    print(f"Graph size: {n}")
    results = {}

    start = time.perf_counter()
    results["greedy"] = greedy_tsp(distance_matrix)
    results["greedy"]["runtime"] = time.perf_counter() - start

    start = time.perf_counter()
    results["heuristic"] = heuristic_tsp(distance_matrix)
    results["heuristic"]["runtime"] = time.perf_counter() - start

    if n <= 12:
        start = time.perf_counter()
        results["dp"] = dp_tsp(distance_matrix)
        results["dp"]["runtime"] = time.perf_counter() - start
    else:
        results["dp"] = "Skipped (too large)"

    return results