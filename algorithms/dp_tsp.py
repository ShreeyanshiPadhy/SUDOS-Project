def dp_tsp(distance_matrix):
    n=len(distance_matrix)
    memo={}
    parent={}

    def visit(mask, pos):
        if mask==(1<<n)-1:
            return distance_matrix[pos][0]

        if (mask, pos) in memo:
            return memo[(mask, pos)]

        ans=float('inf')
        best_city = -1

        for city in range(n):
            if mask & (1<<city)==0:
                new_cost=distance_matrix[pos][city] + visit(mask|(1<<city),city)
                if new_cost < ans:
                    ans = new_cost
                    best_city = city

        memo[(mask, pos)]=ans
        parent[(mask, pos)] = best_city
        return ans

    cost=visit(1, 0)

    # Reconstruct route
    mask = 1
    pos = 0
    route = [0]
    
    for _ in range(n - 1):
        if (mask, pos) in parent:
            next_city = parent[(mask, pos)]
            if next_city == -1:
                break
            route.append(next_city)
            mask |= (1 << next_city)
            pos = next_city
        else:
            break
            
    route.append(0)

    return {
        "route": route,
        "cost": cost
    }