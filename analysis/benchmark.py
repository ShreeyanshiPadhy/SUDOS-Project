"""
Performance Benchmarking Module
Measures execution time, memory usage, and solution quality for TSP algorithms
"""

import time
import tracemalloc
import json
import os
import sys
from typing import Dict, Tuple, List, Any

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.greedy_tsp import greedy_tsp
from algorithms.dp_tsp import dp_tsp
from algorithms.utils import graph_to_distance_matrix
from core.graph import create_small_graph, generate_medium_graph


class BenchmarkMetrics:
    """Stores metrics for a single algorithm run"""
    
    def __init__(self, algorithm_name: str, dataset_name: str, num_nodes: int):
        self.algorithm_name = algorithm_name
        self.dataset_name = dataset_name
        self.num_nodes = num_nodes
        self.execution_time = 0.0  # seconds
        self.memory_used = 0  # bytes
        self.cost = float('inf')
        self.path_length = 0
        self.details = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        # Convert infinity to string for valid JSON
        cost_value = "Infinity" if self.cost == float('inf') else round(self.cost, 2)
        
        return {
            "algorithm": self.algorithm_name,
            "dataset": self.dataset_name,
            "nodes": self.num_nodes,
            "execution_time_ms": round(self.execution_time * 1000, 4),
            "memory_used_mb": round(self.memory_used / (1024 ** 2), 4),
            "solution_cost": cost_value,
            "path_length": self.path_length,
        }


class Benchmark:
    """Benchmark suite for route optimization algorithms"""
    
    def __init__(self):
        self.results: List[BenchmarkMetrics] = []
        self.datasets = {
            "small": None,
            "medium": None,
        }
        self._load_datasets()
    
    def _load_datasets(self):
        """Load or generate test datasets"""
        # Small dataset
        graph, coords = create_small_graph()
        self.datasets["small"] = {
            "graph": graph,
            "coords": coords,
            "num_nodes": len(graph),
            "distance_matrix": graph_to_distance_matrix(graph)
        }
        
        # Medium dataset
        graph, coords = generate_medium_graph(n=50)
        self.datasets["medium"] = {
            "graph": graph,
            "coords": coords,
            "num_nodes": len(graph),
            "distance_matrix": graph_to_distance_matrix(graph)
        }
    
    def benchmark_greedy_tsp(self, distance_matrix: List[List[float]], 
                            dataset_name: str) -> BenchmarkMetrics:
        """Benchmark Greedy TSP algorithm"""
        num_nodes = len(distance_matrix)
        metrics = BenchmarkMetrics("Greedy TSP", dataset_name, num_nodes)
        
        # Start profiling
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Run algorithm
        result = greedy_tsp(distance_matrix, start=0)
        
        # End profiling
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Store metrics
        metrics.execution_time = end_time - start_time
        metrics.memory_used = peak
        metrics.cost = result.get("cost", float('inf'))
        metrics.path_length = len(result.get("route", []))
        
        return metrics
    
    def benchmark_dp_tsp(self, distance_matrix: List[List[float]], 
                        dataset_name: str) -> BenchmarkMetrics:
        """Benchmark DP TSP algorithm"""
        num_nodes = len(distance_matrix)
        metrics = BenchmarkMetrics("DP TSP", dataset_name, num_nodes)
        
        # Start profiling
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Run algorithm
        result = dp_tsp(distance_matrix)
        
        # End profiling
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Store metrics
        metrics.execution_time = end_time - start_time
        metrics.memory_used = peak
        metrics.cost = result.get("cost", float('inf'))
        
        return metrics
    
    def benchmark_all_datasets(self) -> Dict[str, List[BenchmarkMetrics]]:
        """Run all benchmarks on all datasets"""
        results_by_dataset = {}
        
        for dataset_name, dataset_data in self.datasets.items():
            print(f"\n{'='*60}")
            print(f"Benchmarking on {dataset_name.upper()} dataset ({dataset_data['num_nodes']} nodes)")
            print(f"{'='*60}")
            
            distance_matrix = dataset_data["distance_matrix"]
            results_by_dataset[dataset_name] = []
            
            # Benchmark Greedy TSP
            print("Running Greedy TSP...", end=" ", flush=True)
            greedy_metrics = self.benchmark_greedy_tsp(distance_matrix, dataset_name)
            results_by_dataset[dataset_name].append(greedy_metrics)
            print(f"✓ ({greedy_metrics.execution_time*1000:.2f}ms)")
            
            # Benchmark DP TSP (only for small datasets to avoid timeout)
            if dataset_name == "small":
                print("Running DP TSP...", end=" ", flush=True)
                dp_metrics = self.benchmark_dp_tsp(distance_matrix, dataset_name)
                results_by_dataset[dataset_name].append(dp_metrics)
                print(f"✓ ({dp_metrics.execution_time*1000:.2f}ms)")
            else:
                print("Skipping DP TSP (exponential complexity, medium dataset too large)")
            
            self.results.extend(results_by_dataset[dataset_name])
        
        return results_by_dataset
    
    def generate_comparison_table(self) -> str:
        """Generate a formatted comparison table"""
        if not self.results:
            return "No benchmark results available"
        
        # Group by dataset
        by_dataset = {}
        for result in self.results:
            if result.dataset_name not in by_dataset:
                by_dataset[result.dataset_name] = []
            by_dataset[result.dataset_name].append(result)
        
        output = []
        output.append("\n" + "="*100)
        output.append("PERFORMANCE COMPARISON TABLE")
        output.append("="*100)
        
        for dataset_name, metrics_list in by_dataset.items():
            output.append(f"\n{dataset_name.upper()} Dataset ({metrics_list[0].num_nodes} nodes)")
            output.append("-" * 100)
            output.append(f"{'Algorithm':<20} {'Time (ms)':<15} {'Memory (MB)':<15} {'Solution Cost':<15} {'Path Length':<15}")
            output.append("-" * 100)
            
            for metrics in metrics_list:
                output.append(
                    f"{metrics.algorithm_name:<20} "
                    f"{metrics.execution_time*1000:>13.4f}  "
                    f"{metrics.memory_used/(1024**2):>13.4f}  "
                    f"{metrics.cost:>13.2f}  "
                    f"{metrics.path_length:>13}"
                )
            
            # Calculate gaps if both algorithms exist
            if len(metrics_list) > 1:
                greedy = next((m for m in metrics_list if "Greedy" in m.algorithm_name), None)
                dp = next((m for m in metrics_list if "DP" in m.algorithm_name), None)
                
                if greedy and dp:
                    cost_gap = ((greedy.cost - dp.cost) / dp.cost * 100) if dp.cost > 0 else 0
                    time_ratio = greedy.execution_time / dp.execution_time if dp.execution_time > 0 else 0
                    output.append("-" * 100)
                    output.append(f"Greedy vs DP: Cost Gap = {cost_gap:.2f}% | Speed Ratio (Greedy/DP) = {time_ratio:.2f}x")
        
        output.append("="*100)
        return "\n".join(output)
    
    def generate_scalability_analysis(self) -> str:
        """Analyze algorithm scalability across dataset sizes"""
        output = []
        output.append("\n" + "="*80)
        output.append("SCALABILITY ANALYSIS")
        output.append("="*80)
        
        # Group by algorithm
        by_algorithm = {}
        for result in self.results:
            if result.algorithm_name not in by_algorithm:
                by_algorithm[result.algorithm_name] = []
            by_algorithm[result.algorithm_name].append(result)
        
        for algo_name, metrics_list in by_algorithm.items():
            sorted_metrics = sorted(metrics_list, key=lambda m: m.num_nodes)
            output.append(f"\n{algo_name}")
            output.append("-" * 80)
            output.append(f"{'Nodes':<10} {'Time (ms)':<15} {'Memory (MB)':<15} {'Cost':<15}")
            output.append("-" * 80)
            
            for metrics in sorted_metrics:
                output.append(
                    f"{metrics.num_nodes:<10} "
                    f"{metrics.execution_time*1000:>13.4f}  "
                    f"{metrics.memory_used/(1024**2):>13.4f}  "
                    f"{metrics.cost:>13.2f}"
                )
            
            # Analyze growth pattern
            if len(sorted_metrics) >= 2:
                m1 = sorted_metrics[0]
                m2 = sorted_metrics[-1]
                time_growth = (m2.execution_time / m1.execution_time) ** (1 / (m2.num_nodes - m1.num_nodes))
                output.append(f"\nTime Growth Factor: {time_growth:.4f}x per node")
                
                complexity = "O(n²)" if time_growth < 1.1 else "O(n³)" if time_growth < 1.2 else "Exponential"
                output.append(f"Estimated Complexity: {complexity}")
        
        output.append("="*80)
        return "\n".join(output)
    
    def save_results(self, output_file: str = "analysis/benchmark_results.json"):
        """Save benchmark results to JSON file"""
        results_dict = [r.to_dict() for r in self.results]
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n✓ Results saved to {output_file}")
    
    def print_summary(self):
        """Print comprehensive benchmark summary"""
        print(self.generate_comparison_table())
        print(self.generate_scalability_analysis())


if __name__ == "__main__":
    benchmark = Benchmark()
    results = benchmark.benchmark_all_datasets()
    benchmark.print_summary()
    benchmark.save_results()
