def graph_to_distance_matrix(graph):
    n=len(graph)
    dist=[[float('inf')]*n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
        for neighbor, weight in graph[str(i)]:
            dist[i][int(neighbor)] = weight

    return dist