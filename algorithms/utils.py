def graph_to_distance_matrix(graph):
    n=len(graph)
    dist=[[float('inf')]*n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
        # Handle both integer and string keys
        key = i if i in graph else str(i)
        if key in graph:
            for neighbor, weight in graph[key]:
                # Convert neighbor to int for indexing
                neighbor_idx = int(neighbor) if isinstance(neighbor, str) else neighbor
                dist[i][neighbor_idx] = weight

    # Floyd-Warshall to find all-pairs shortest paths
    # This guarantees the graph is complete so TSP algorithms don't hit "Infinity" cost
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist