from core.graph import GraphLoader

loader = GraphLoader()  # not used

loader.load_osm_graph()
loader.preprocess_graph()
loader.convert_to_adjacency_list()
loader.apply_traffic()

loader.print_stats()
loader.save("datasets/large_graph.json")