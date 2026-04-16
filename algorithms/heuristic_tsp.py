def heuristic_tsp(distance_matrix):
    n = len(distance_matrix)

    if n == 0:
        return {"route": [], "cost": 0}

    # Step 1: start with node 0
    route = [0, 0]  # start and end same
    visited = set([0])

    # Step 2: pick nearest node to start
    nearest = None
    min_dist = float('inf')

    for i in range(1, n):
        if distance_matrix[0][i] < min_dist:
            min_dist = distance_matrix[0][i]
            nearest = i

    route = [0, nearest, 0]
    visited.add(nearest)

    # Step 3: insert remaining nodes
    while len(visited) < n:
        best_node = None
        best_position = None
        min_increase = float('inf')

        for node in range(n):
            if node in visited:
                continue

            # try inserting node between every pair
            for i in range(len(route) - 1):
                a = route[i]
                b = route[i + 1]

                if (
                    distance_matrix[a][node] == float('inf') or
                    distance_matrix[node][b] == float('inf')
                ):
                    continue
                cost_increase = (
                    distance_matrix[a][node]
                    + distance_matrix[node][b]
                    - distance_matrix[a][b]
                )

                if cost_increase < min_increase:
                    min_increase = cost_increase
                    best_node = node
                    best_position = i + 1
        if best_node is None:
            print("WARNING: Graph disconnected, skipping remaining nodes")
            break
        route.insert(best_position, best_node)
        visited.add(best_node)

    # Step 4: compute total cost
    total_cost = 0
    for i in range(len(route) - 1):
        total_cost += distance_matrix[route[i]][route[i + 1]]

    return {
        "route": route,
        "cost": total_cost
    }