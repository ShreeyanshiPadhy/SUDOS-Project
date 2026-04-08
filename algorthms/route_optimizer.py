from algorthms.greedy_tsp import greedy_tsp
from algorthms.dp_tsp import dp_tsp

def run_tsp_algorithms(distance_matrix):
    greedy_result=greedy_tsp(distance_matrix)
    dp_result=dp_tsp(distance_matrix)

    return {
        "greedy": greedy_result,
        "dp": dp_result
    }