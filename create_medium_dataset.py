from core.graph import generate_medium_graph
import json

graph, coords = generate_medium_graph(50)

with open("datasets/medium_graph.json", "w") as f:
    json.dump({
        "graph": graph,
        "coordinates": coords
    }, f)

print("Medium dataset created!")