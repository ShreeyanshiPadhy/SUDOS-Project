from core.graph import create_small_graph
import json

graph, coords = create_small_graph()

with open("datasets/small_graph.json", "w") as f:
    json.dump({
        "graph": graph,
        "coordinates": coords
    }, f)

print("Small dataset created!")