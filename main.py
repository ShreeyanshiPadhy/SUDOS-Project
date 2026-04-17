import json
import argparse
import logging
import sys
import os
import time

from algorithms.route_optimizer import run_tsp_algorithms

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Run SUDOS Algorithms")
    parser.add_argument("--dataset", type=str, default="datasets/small_graph.json")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--report", action="store_true", help="Generate interactive HTML report at ui/sudos_report.html")

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
    MAX_NODES = 100

    # First, make the entire graph symmetric so BFS extracts a traversable area
    symmetric_graph = {node: [] for node in graph}
    for u in graph:
        for v, w in graph[u]:
            symmetric_graph[u].append((v, w))
            if v in symmetric_graph:
                # Add reverse edge if missing to avoid one-way dead ends
                if u not in [neigh for neigh, _ in symmetric_graph[v]]:
                    symmetric_graph[v].append((u, w))
    graph = symmetric_graph

    start = list(graph.keys())[0]
    visited = set([start])
    queue = [start]

    while queue and len(visited) < MAX_NODES:
        node = queue.pop(0)
        for neigh, _ in graph[node]:
            if neigh not in visited:
                visited.add(neigh)
                queue.append(neigh)

    selected_nodes = sorted(list(visited))

    # Filter graph strictly to the selected subgraph
    graph = {
        node: [(neigh, w) for neigh, w in graph[node] if neigh in selected_nodes]
        for node in selected_nodes
    }
    
    # Re-map node IDs to 0..N-1 for matrix indexing
    node_to_idx = {node: i for i, node in enumerate(selected_nodes)}
    idx_graph = {node_to_idx[u]: [(node_to_idx[v], w) for v, w in graph[u]] for u in selected_nodes}
    graph = idx_graph # Use sequential indices for TSP consistency
    
    logging.info(f"Loaded dataset: {args.dataset} (Sanitized to {len(selected_nodes)} connected nodes)")

    # 🔥 USE DIJKSTRA (IMPORTANT)
    logging.info("Running Dijkstra (all-pairs shortest paths)...")
    from algorithms.dijkstra import get_distance_matrix
    t0 = time.perf_counter()
    distance_matrix, predecessor_matrix = get_distance_matrix(graph)
    dijkstra_time = time.perf_counter() - t0
    
    # Safe float conversion for JSON (replace inf with large number)
    SAFE_INF = 999999.0
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix[i])):
            if distance_matrix[i][j] == float('inf'): distance_matrix[i][j] = SAFE_INF

    if args.verbose:
        logging.info("Distance Matrix processed.")

    logging.info("Running TSP algorithms...")
    results = run_tsp_algorithms(distance_matrix)

    print("\n--- PERFORMANCE RESULTS ---")
    print(f"Greedy:    {results.get('greedy')}")
    if "heuristic" in results: print(f"Heuristic: {results.get('heuristic')}")
    print(f"DP:        {results.get('dp')}")

    if args.report:
        # Use the original coordinates from the data but pass the selected node IDs
        coords_subset = {}
        original_node_ids = selected_nodes 
        for i, nid in enumerate(original_node_ids):
            coords_subset[str(i)] = data.get("coordinates", {}).get(str(nid), [0, 0])
        
        generate_html_report(args.dataset, coords_subset, graph, results, distance_matrix, predecessor_matrix, dijkstra_time)

def generate_html_report(ds_name, coords, graph_edges, results, dist_matrix, pred_matrix, dijkstra_runtime):
    import json
    import math
    
    # mapping node id to index
    node_list = list(graph_edges.keys())
    
    # Generate NODES
    nodes = []
    # fallback check if all coordinates in dataset are missing/zero
    all_zero = all(coords.get(str(n), [0, 0]) == [0, 0] for n in node_list)
    
    for i, node_id in enumerate(node_list):
        if all_zero:
            nodes.append({"x": 0, "y": 0, "label": f"N{i}", "name": f"Node {i}"})
        else:
            p = coords.get(str(node_id), [0, 0])
            nodes.append({
                "x": p[0],
                "y": p[1],
                "label": f"N{i}",
                "name": f"Node {i}"
            })
        
    # Generate EDGES
    edges = []
    for node, connects in graph_edges.items():
        try:
            u_idx = node_list.index(node)
            for neigh, weight in connects:
                v_idx = node_list.index(neigh)
                if u_idx < v_idx: edges.append([u_idx, v_idx, weight])
        except ValueError: pass

    # Generate ALGOS
    algos = {}
    
    # Add Dijkstra foundation
    algos["dijkstra"] = {
        "title": "Shortest Paths (Dijkstra)",
        "dist": "N/A",
        "time": "O(E log V)",
        "runtime": f"{dijkstra_runtime * 1000:.2f} ms",
        "routes": []
    }
    
    # TSP result mapping
    for k in ["greedy", "heuristic", "dp"]:
        if k in results and isinstance(results[k], dict):
            res = results[k]
            path = res.get("route", [])
            # Skip if path not reconstructed
            if not isinstance(path, list) or len(path) == 0: continue
            
            algos[k] = {
                "title": k.capitalize() + " TSP",
                "dist": f"{float(res['cost']):.1f}",
                "time": "O(N²)" if k != "dp" else "O(2ⁿ N²)",
                "runtime": f"{res.get('runtime', 0) * 1000:.2f} ms",
                "routes": [{"color": "#185FA5", "nodes": path}]
            }
        elif k in results and results[k] == "Skipped (too large)":
             algos[k] = {
                "title": k.capitalize() + " TSP", "dist": "Skipped", "time": "O(2ⁿ N²)", "runtime": "N/A", "routes": []
            }

    sudos_data = {
        "NODES": nodes,
        "EDGES": edges,
        "ALGOS": algos,
        "MATRIX": dist_matrix,
        "PREDECESSORS": pred_matrix
    }
    
    js_payload = json.dumps(sudos_data)
    template_path = os.path.join("ui", "template.html")
    report_path = os.path.join("ui", "sudos_report.html")
    
    if not os.path.exists(template_path):
        logging.error("Could not find ui/template.html")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read().replace("<!-- INJECT_SUDOS_DATA -->", js_payload)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    logging.info(f"Report generated successfully: {report_path}")

if __name__ == "__main__":
    main()