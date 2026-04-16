def greedy_tsp(distance_matrix, start=0):
    n=len(distance_matrix)
    visited=[False]*n
    route=[start]
    visited[start]=True
    total_cost=0

    current=start

    for _ in range(n - 1):
        next_node=None
        min_dist=float('inf')

        for j in range(n):
            if not visited[j] and distance_matrix[current][j] < min_dist:
                min_dist=distance_matrix[current][j]
                next_node=j
        if next_node is None:
            print("ERROR: Graph may be disconnected or distance matrix incorrect")
            return {
                "route": route,
                "cost": float('inf')
            }
        route.append(next_node)
        visited[next_node]=True
        total_cost+=min_dist
        current=next_node

    total_cost+=distance_matrix[current][start]
    route.append(start)

    return {
        "route": route,
        "cost": total_cost
    }