import argparse
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph import create_small_graph, generate_medium_graph, GraphLoader


def main():
    parser = argparse.ArgumentParser(description="Generate datasets for SUDOS")
    parser.add_argument("--size", type=str, choices=["small", "medium", "large"], required=True, help="Size of the dataset to generate")
    args = parser.parse_args()

    os.makedirs("datasets", exist_ok=True)

    if args.size == "small":
        graph, coords = create_small_graph()
        with open("datasets/small_graph.json", "w") as f:
            json.dump({"graph": graph, "coordinates": coords}, f)
        print("Small dataset created!")

    elif args.size == "medium":
        graph, coords = generate_medium_graph(50)
        with open("datasets/medium_graph.json", "w") as f:
            json.dump({"graph": graph, "coordinates": coords}, f)
        print("Medium dataset created!")

    elif args.size == "large":
        loader = GraphLoader()
        loader.load_osm_graph()
        loader.preprocess_graph()
        loader.convert_to_adjacency_list()
        loader.apply_traffic()
        loader.print_stats()
        loader.save("datasets/large_graph.json")
        print("Large dataset created!")

if __name__ == "__main__":
    main()
