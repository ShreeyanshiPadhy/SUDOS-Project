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

    selected_nodes = visited

    # Filter graph strictly to the selected subgraph
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

    if "heuristic" in results:
        print(f"Heuristic: {results.get('heuristic')}")

    print(f"DP:        {results.get('dp')}")

    if args.report:
        generate_html_report(args.dataset, data.get("coordinates", {}), graph, results)

def generate_html_report(ds_name, coords, graph_edges, results):
    import json
    import math
    
    # Generate NODES
    nodes = []
    # mapping node id to index
    node_list = list(graph_edges.keys())
    
    # fallback check if all coordinates in dataset are missing/zero
    all_zero = all(coords.get(str(n), [0, 0]) == [0, 0] for n in node_list)
    
    for i, node_id in enumerate(node_list):
        if all_zero:
            # Generate a nice circular layout
            angle = i * (2 * math.pi / len(node_list))
            pos = [50 + 40 * math.cos(angle), 50 + 40 * math.sin(angle)]
        else:
            pos = coords.get(str(node_id), [0, 0])
            
        nodes.append({
            "x": pos[0],
            "y": pos[1],
            "label": f"N{node_id}",
            "name": f"Node {node_id}"
        })
        
    # Generate EDGES
    edges = []
    for node, connects in graph_edges.items():
        node_idx = node_list.index(node)
        for neigh, weight in connects:
            try:
                neigh_idx = node_list.index(neigh)
                edges.append([node_idx, neigh_idx, weight])
            except ValueError:
                pass

    # Generate ALGOS
    algos = {}
    
    # We map what results returns to the JS format
    if "greedy" in results and isinstance(results["greedy"], dict):
        # Convert path IDs to array indices
        path_idx = [node_list.index(n) for n in results["greedy"]["route"] if n in node_list]
        chips = [f"{path_idx[i]}→{path_idx[i+1]}" for i in range(len(path_idx)-1)]
        algos["greedy"] = {
            "title": "Greedy Nearest Neighbor",
            "dist": f"{results['greedy']['cost']} units",
            "distSub": "Fast heuristic route",
            "time": "O(n²)",
            "runtime": f"{results['greedy'].get('runtime', 0) * 1000:.2f} ms",
            "routes": [{"color": "#185FA5", "nodes": path_idx, "label": "Greedy Tour"}],
            "chips": chips
        }
        
    if "heuristic" in results and isinstance(results["heuristic"], dict):
        path_idx = [node_list.index(n) for n in results["heuristic"]["route"] if n in node_list]
        chips = [f"{path_idx[i]}→{path_idx[i+1]}" for i in range(len(path_idx)-1)]
        algos["heuristic"] = {
            "title": "Insertion Heuristic TSP",
            "dist": f"{results['heuristic']['cost']} units",
            "distSub": "Less than 2x optimal",
            "time": "O(n² log n)",
            "runtime": f"{results['heuristic'].get('runtime', 0) * 1000:.2f} ms",
            "routes": [{"color": "#BA7517", "nodes": path_idx, "label": "Heuristic Tour"}],
            "chips": chips
        }
        
    if "dp" in results:
        if isinstance(results["dp"], dict):
            # Route might be "Not reconstructed"
            path_idx = []
            chips = []
            if isinstance(results["dp"].get("route"), list):
                path_idx = [node_list.index(n) for n in results["dp"]["route"] if n in node_list]
                chips = [f"{path_idx[i]}→{path_idx[i+1]}" for i in range(len(path_idx)-1)]
            
            algos["dp"] = {
                "title": "DP-TSP (Exact)",
                "dist": f"{results['dp']['cost']} units",
                "distSub": "Guaranteed globally optimal",
                "time": "O(2ⁿ·n²)",
                "runtime": f"{results['dp'].get('runtime', 0) * 1000:.2f} ms",
                "routes": [{"color": "#639922", "nodes": path_idx, "label": "Optimal Tour"}],
                "chips": chips
            }
        else:
            algos["dp"] = {
                "title": "DP-TSP (Exact)",
                "dist": "Skipped",
                "distSub": "Dataset too large for Exact DP",
                "time": "O(2ⁿ·n²)",
                "runtime": "N/A",
                "routes": [{"color": "#639922", "nodes": [], "label": "Skipped"}],
                "chips": ["Dataset too large", "|", "O(2ⁿ) complexity avoids freezing the system"]
            }

    sudos_data = {
        "NODES": nodes,
        "EDGES": edges,
        "ALGOS": algos
    }
    
    js_payload = json.dumps(sudos_data)
    
    template_path = os.path.join("ui", "template.html")
    report_path = os.path.join("ui", "sudos_report.html")
    
    if not os.path.exists(template_path):
        logging.error("Could not find ui/template.html. Start by creating the template.")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    html = html.replace("<!-- INJECT_SUDOS_DATA -->", js_payload)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    logging.info(f"Report generated successfully: {report_path}")

if __name__ == "__main__":
    main()