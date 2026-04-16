"""
Analysis Runner - Main orchestrator for algorithm analysis
Coordinates benchmarking, visualization, and report generation
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.benchmark import Benchmark
from analysis.charts import ChartGenerator


class AnalysisRunner:
    """Orchestrate complete analysis workflow"""
    
    def __init__(self):
        self.results_dir = "analysis/results"
        self.benchmark_file = f"{self.results_dir}/benchmark_results.json"
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
    
    def run_benchmarks(self) -> bool:
        """Execute benchmark suite"""
        try:
            print("\n" + "="*80)
            print("PHASE 1: BENCHMARKING")
            print("="*80)
            
            benchmark = Benchmark()
            results = benchmark.benchmark_all_datasets()
            benchmark.print_summary()
            benchmark.save_results(self.benchmark_file)
            
            print("\n✓ Benchmarking phase completed successfully")
            return True
        except Exception as e:
            print(f"✗ Benchmarking failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_visualizations(self) -> bool:
        """Generate charts and visualizations"""
        try:
            print("\n" + "="*80)
            print("PHASE 2: VISUALIZATION")
            print("="*80)
            
            generator = ChartGenerator(self.benchmark_file)
            generator.generate_all_charts()
            generator.generate_report_html()
            
            print("\n✓ Visualization phase completed successfully")
            return True
        except Exception as e:
            print(f"✗ Visualization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_summary_report(self) -> bool:
        """Generate text summary report"""
        try:
            print("\n" + "="*80)
            print("PHASE 3: REPORT GENERATION")
            print("="*80)
            
            with open(self.benchmark_file) as f:
                results = json.load(f)
            
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("SUDOS - ALGORITHM PERFORMANCE ANALYSIS REPORT")
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("=" * 80)
            
            # Summary statistics
            report_lines.append("\n📋 SUMMARY STATISTICS")
            report_lines.append("-" * 80)
            
            by_algo = {}
            for result in results:
                algo = result["algorithm"]
                if algo not in by_algo:
                    by_algo[algo] = {"count": 0, "total_time": 0, "total_cost": 0, "nodes": [], "has_infinity": False}
                by_algo[algo]["count"] += 1
                by_algo[algo]["total_time"] += result["execution_time_ms"]
                # Only add to total_cost if numeric, otherwise mark as having infinity
                if isinstance(result["solution_cost"], str) or result["solution_cost"] == float('inf'):
                    by_algo[algo]["has_infinity"] = True
                else:
                    by_algo[algo]["total_cost"] += result["solution_cost"]
                by_algo[algo]["nodes"].append(result["nodes"])
            
            for algo, stats in sorted(by_algo.items()):
                avg_time = stats["total_time"] / stats["count"]
                nodes_tested = ", ".join(map(str, sorted(set(stats["nodes"]))))
                
                report_lines.append(f"\n{algo}:")
                report_lines.append(f"  Datasets tested: {stats['count']}")
                report_lines.append(f"  Average time: {avg_time:.4f} ms")
                if stats["has_infinity"]:
                    report_lines.append(f"  Average cost: Infinity (disconnected graphs)")
                else:
                    avg_cost = stats["total_cost"] / stats["count"]
                    report_lines.append(f"  Average cost: {avg_cost:.2f}")
                report_lines.append(f"  Nodes tested: {nodes_tested}")
            
            # Detailed results
            report_lines.append("\n\n📊 DETAILED RESULTS BY DATASET")
            report_lines.append("-" * 80)
            
            by_dataset = {}
            for result in results:
                dataset = result["dataset"]
                if dataset not in by_dataset:
                    by_dataset[dataset] = []
                by_dataset[dataset].append(result)
            
            for dataset in sorted(by_dataset.keys()):
                report_lines.append(f"\n{dataset.upper()} Dataset:")
                report_lines.append(f"{'Algorithm':<20} {'Time (ms)':<15} {'Memory (MB)':<15} {'Cost':<15}")
                report_lines.append("-" * 65)
                
                for result in sorted(by_dataset[dataset], key=lambda r: r["algorithm"]):
                    # Format cost as string if it's "Infinity", otherwise as numeric
                    cost_str = str(result['solution_cost']) if isinstance(result['solution_cost'], str) else f"{result['solution_cost']:>13.2f}"
                    report_lines.append(
                        f"{result['algorithm']:<20} "
                        f"{result['execution_time_ms']:>13.4f}  "
                        f"{result['memory_used_mb']:>13.4f}  "
                        f"{cost_str:>13}"
                    )
                
                # Calculate gap if comparing greedy and DP
                greedy_result = next((r for r in by_dataset[dataset] if "Greedy" in r["algorithm"]), None)
                dp_result = next((r for r in by_dataset[dataset] if "DP" in r["algorithm"]), None)
                
                if greedy_result and dp_result:
                    greedy_cost = greedy_result["solution_cost"]
                    dp_cost = dp_result["solution_cost"]
                    # Only calculate gap if both are numeric (not "Infinity" strings)
                    if isinstance(greedy_cost, (int, float)) and isinstance(dp_cost, (int, float)):
                        cost_gap = ((greedy_cost - dp_cost) / dp_cost) * 100
                        report_lines.append(f"\nAlgorithm Comparison:")
                        report_lines.append(f"  Greedy solution is {cost_gap:.2f}% worse than DP (Optimal)")
                    else:
                        report_lines.append(f"\nAlgorithm Comparison:")
                        report_lines.append(f"  Note: Cost comparison not available (Infinity values)")
                    
                    if greedy_result["execution_time_ms"] > 0:
                        speedup = dp_result["execution_time_ms"] / greedy_result["execution_time_ms"]
                        report_lines.append(f"  Greedy is {speedup:.2f}x faster than DP")
            
            # Recommendations
            report_lines.append("\n\n💡 RECOMMENDATIONS")
            report_lines.append("-" * 80)
            
            # Find fastest algorithm
            fastest = min(results, key=lambda r: r["execution_time_ms"])
            report_lines.append(f"• Fastest algorithm: {fastest['algorithm']} ({fastest['execution_time_ms']:.4f} ms)")
            
            # Find best quality (filter out "Infinity" string values)
            numeric_results = [r for r in results if isinstance(r.get("solution_cost"), (int, float))]
            if numeric_results:
                best_quality = min(numeric_results, key=lambda r: r["solution_cost"])
                report_lines.append(f"• Best solution quality: {best_quality['algorithm']} (cost: {best_quality['solution_cost']:.2f})")
            else:
                report_lines.append(f"• Best solution quality: N/A (all results are Infinity)")
            
            # Memory efficient
            least_memory = min(results, key=lambda r: r["memory_used_mb"])
            report_lines.append(f"• Most memory efficient: {least_memory['algorithm']} ({least_memory['memory_used_mb']:.4f} MB)")
            
            report_lines.append("\n• For real-time delivery requests: Use Greedy TSP (fast, good enough)")
            report_lines.append("• For optimal planning with small datasets: Use DP TSP")
            report_lines.append("• For balanced performance: Consider hybrid approach based on dataset size")
            
            report_lines.append("\n" + "=" * 80)
            report_lines.append("END OF REPORT")
            report_lines.append("=" * 80)
            
            # Save report
            report_text = "\n".join(report_lines)
            report_file = f"{self.results_dir}/analysis_report.txt"
            with open(report_file, "w", encoding='utf-8') as f:
                f.write(report_text)
            
            print(report_text)
            print(f"\n✓ Report saved to: {report_file}")
            print(f"✓ Visualizations saved to: analysis/charts/")
            print(f"✓ Raw results saved to: {self.benchmark_file}")
            
            return True
        except Exception as e:
            print(f"✗ Report generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline"""
        print("\n" + "🔍 " * 20)
        print("SUDOS - ALGORITHM PERFORMANCE ANALYSIS")
        print("🔍 " * 20)
        
        success = True
        
        # Phase 1: Benchmark
        if not self.run_benchmarks():
            success = False
        
        # Phase 2: Visualize
        if success and not self.generate_visualizations():
            success = False
        
        # Phase 3: Report
        if success and not self.generate_summary_report():
            success = False
        
        # Summary
        print("\n" + "="*80)
        if success:
            print("✓ ANALYSIS COMPLETED SUCCESSFULLY")
            print("="*80)
            print("\nGenerated Outputs:")
            print("  • analysis/results/benchmark_results.json - Raw benchmark data")
            print("  • analysis/results/analysis_report.txt - Text report")
            print("  • analysis/charts/ - Visualization charts")
            print("  • analysis/charts/report.html - Interactive HTML report")
        else:
            print("✗ ANALYSIS FAILED - CHECK ERRORS ABOVE")
            print("="*80)
            sys.exit(1)


if __name__ == "__main__":
    runner = AnalysisRunner()
    runner.run_complete_analysis()
