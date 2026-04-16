def dp_tsp(distance_matrix):
    n=len(distance_matrix)
    memo={}

    def visit(mask, pos):
        if mask==(1<<n)-1:
            return distance_matrix[pos][0]

        if (mask, pos) in memo:
            return memo[(mask, pos)]

        ans=float('inf')

        for city in range(n):
            if mask & (1<<city)==0:
                new_cost=distance_matrix[pos][city] + visit(mask|(1<<city),city)
                ans=min(ans, new_cost)

        memo[(mask, pos)]=ans
        return ans

    cost=visit(1, 0)

    return {
        "route": "Not reconstructed",
        "cost": cost
    }