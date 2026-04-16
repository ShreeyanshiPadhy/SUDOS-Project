"""
Data Visualization Module
Creates charts and graphs to compare algorithm performance
"""

import json
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ChartGenerator:
    """Generate visualization charts for algorithm comparison"""
    
    def __init__(self, results_file: str = "analysis/benchmark_results.json"):
        self.results_file = results_file
        self.results = self._load_results()
        self.colors = {
            "Greedy TSP": "#FF6B6B",
            "DP TSP": "#4ECDC4",
            "Heuristic TSP": "#45B7D1"
        }
        self.output_dir = "analysis/charts"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_results(self) -> List[Dict]:
        """Load benchmark results from JSON"""
        try:
            with open(self.results_file) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠ Results file not found: {self.results_file}")
            return []
    
    def chart_execution_time_comparison(self):
        """Bar chart: Execution time comparison by algorithm and dataset"""
        if not self.results:
            print("No results to plot")
            return
        
        # Group by dataset
        by_dataset = {}
        for result in self.results:
            dataset = result["dataset"]
            if dataset not in by_dataset:
                by_dataset[dataset] = {}
            by_dataset[dataset][result["algorithm"]] = result["execution_time_ms"]
        
        fig, axes = plt.subplots(1, len(by_dataset), figsize=(14, 5))
        if len(by_dataset) == 1:
            axes = [axes]
        
        for idx, (dataset, algos) in enumerate(by_dataset.items()):
            ax = axes[idx]
            algorithms = list(algos.keys())
            times = list(algos.values())
            colors_list = [self.colors.get(algo, "#888888") for algo in algorithms]
            
            bars = ax.bar(algorithms, times, color=colors_list, edgecolor="black", linewidth=1.5)
            ax.set_title(f"{dataset.capitalize()} Dataset ({self.results[0]['nodes']} nodes)", fontsize=12, fontweight="bold")
            ax.set_ylabel("Execution Time (ms)", fontsize=11)
            ax.set_xlabel("Algorithm", fontsize=11)
            ax.grid(axis="y", alpha=0.3, linestyle="--")
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}ms',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        filepath = f"{self.output_dir}/execution_time_comparison.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def chart_solution_quality_comparison(self):
        """Bar chart: Solution cost comparison (for TSP algorithms)"""
        if not self.results:
            return
        
        # Filter results with numeric solution costs (exclude "Infinity" strings)
        results_with_cost = [r for r in self.results 
                           if r.get("solution_cost") != "Infinity" 
                           and r.get("solution_cost", float('inf')) != float('inf')]
        if not results_with_cost:
            print("⚠ No solution cost data available")
            return
        
        by_dataset = {}
        for result in results_with_cost:
            dataset = result["dataset"]
            if dataset not in by_dataset:
                by_dataset[dataset] = {}
            by_dataset[dataset][result["algorithm"]] = result["solution_cost"]
        
        fig, axes = plt.subplots(1, len(by_dataset), figsize=(14, 5))
        if len(by_dataset) == 1:
            axes = [axes]
        
        for idx, (dataset, algos) in enumerate(by_dataset.items()):
            ax = axes[idx]
            algorithms = list(algos.keys())
            costs = list(algos.values())
            colors_list = [self.colors.get(algo, "#888888") for algo in algorithms]
            
            bars = ax.bar(algorithms, costs, color=colors_list, edgecolor="black", linewidth=1.5)
            ax.set_title(f"{dataset.capitalize()} Dataset", fontsize=12, fontweight="bold")
            ax.set_ylabel("Solution Cost", fontsize=11)
            ax.set_xlabel("Algorithm", fontsize=11)
            ax.grid(axis="y", alpha=0.3, linestyle="--")
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=9)
            
            # Add gap percentage if comparing greedy and DP (and both are numeric)
            if "Greedy TSP" in algos and "DP TSP" in algos:
                greedy_cost = algos["Greedy TSP"]
                dp_cost = algos["DP TSP"]
                # Only calculate gap if both are numeric
                if isinstance(greedy_cost, (int, float)) and isinstance(dp_cost, (int, float)):
                    gap = ((greedy_cost - dp_cost) / dp_cost) * 100
                    ax.text(0.5, 0.95, f"Greedy Gap: {gap:.2f}%", 
                           transform=ax.transAxes, fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.7),
                           ha="center", va="top")
        
        plt.tight_layout()
        filepath = f"{self.output_dir}/solution_quality_comparison.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def chart_memory_usage_comparison(self):
        """Bar chart: Memory usage comparison"""
        if not self.results:
            return
        
        by_dataset = {}
        for result in self.results:
            dataset = result["dataset"]
            if dataset not in by_dataset:
                by_dataset[dataset] = {}
            by_dataset[dataset][result["algorithm"]] = result["memory_used_mb"]
        
        fig, axes = plt.subplots(1, len(by_dataset), figsize=(14, 5))
        if len(by_dataset) == 1:
            axes = [axes]
        
        for idx, (dataset, algos) in enumerate(by_dataset.items()):
            ax = axes[idx]
            algorithms = list(algos.keys())
            memory = list(algos.values())
            colors_list = [self.colors.get(algo, "#888888") for algo in algorithms]
            
            bars = ax.bar(algorithms, memory, color=colors_list, edgecolor="black", linewidth=1.5)
            ax.set_title(f"{dataset.capitalize()} Dataset", fontsize=12, fontweight="bold")
            ax.set_ylabel("Memory Usage (MB)", fontsize=11)
            ax.set_xlabel("Algorithm", fontsize=11)
            ax.grid(axis="y", alpha=0.3, linestyle="--")
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.4f}MB',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        filepath = f"{self.output_dir}/memory_usage_comparison.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def chart_time_vs_quality_tradeoff(self):
        """Scatter plot: Speed vs Quality trade-off"""
        if not self.results:
            return
        
        # Filter results with numeric solution costs (exclude "Infinity" strings)
        results_with_cost = [r for r in self.results 
                           if r.get("solution_cost") != "Infinity" 
                           and r.get("solution_cost", float('inf')) != float('inf')]
        if len(results_with_cost) < 2:
            print("⚠ Insufficient data for trade-off analysis")
            return
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        by_algo = {}
        for result in results_with_cost:
            algo = result["algorithm"]
            if algo not in by_algo:
                by_algo[algo] = []
            by_algo[algo].append(result)
        
        for algo, results_list in by_algo.items():
            times = [r["execution_time_ms"] for r in results_list]
            costs = [r["solution_cost"] for r in results_list]
            color = self.colors.get(algo, "#888888")
            
            ax.scatter(times, costs, s=200, color=color, alpha=0.7, edgecolors="black", linewidth=2, label=algo)
            
            # Connect points with lines if multiple datasets
            if len(times) > 1:
                sorted_indices = np.argsort(times)
                sorted_times = [times[i] for i in sorted_indices]
                sorted_costs = [costs[i] for i in sorted_indices]
                ax.plot(sorted_times, sorted_costs, color=color, alpha=0.4, linestyle="--")
        
        ax.set_xlabel("Execution Time (ms)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Solution Cost", fontsize=12, fontweight="bold")
        ax.set_title("Speed vs Quality Trade-off", fontsize=14, fontweight="bold")
        ax.legend(fontsize=11, loc="best")
        ax.grid(True, alpha=0.3, linestyle="--")
        
        plt.tight_layout()
        filepath = f"{self.output_dir}/time_vs_quality_tradeoff.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def chart_complexity_analysis(self):
        """Line chart: Scalability analysis - Time growth with dataset size"""
        if not self.results:
            return
        
        # Group by algorithm
        by_algo = {}
        for result in self.results:
            algo = result["algorithm"]
            if algo not in by_algo:
                by_algo[algo] = []
            by_algo[algo].append(result)
        
        fig, ax = plt.subplots(figsize=(11, 7))
        
        for algo, results_list in by_algo.items():
            sorted_results = sorted(results_list, key=lambda r: r["nodes"])
            nodes = [r["nodes"] for r in sorted_results]
            times = [r["execution_time_ms"] for r in sorted_results]
            color = self.colors.get(algo, "#888888")
            
            ax.plot(nodes, times, marker="o", linewidth=2.5, markersize=8, 
                   color=color, label=algo, alpha=0.8)
            
            # Add value labels
            for node, time in zip(nodes, times):
                ax.text(node, time, f'{time:.2f}ms', fontsize=9, ha='center', va='bottom')
        
        ax.set_xlabel("Number of Nodes", fontsize=12, fontweight="bold")
        ax.set_ylabel("Execution Time (ms)", fontsize=12, fontweight="bold")
        ax.set_title("Algorithm Scalability: Time vs Problem Size", fontsize=14, fontweight="bold")
        ax.legend(fontsize=11, loc="best")
        ax.grid(True, alpha=0.3, linestyle="--")
        
        plt.tight_layout()
        filepath = f"{self.output_dir}/complexity_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def chart_performance_summary_table(self):
        """Create a summary table visualization"""
        if not self.results:
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.axis("tight")
        ax.axis("off")
        
        # Prepare table data
        table_data = []
        table_data.append(["Algorithm", "Dataset", "Nodes", "Time (ms)", "Memory (MB)", "Cost"])
        
        for result in sorted(self.results, key=lambda r: (r["dataset"], r["algorithm"])):
            # Format cost: handle both "Infinity" strings and numeric values
            cost_str = result['solution_cost']
            if isinstance(cost_str, str):
                cost_display = cost_str  # Already a string like "Infinity"
            elif cost_str == float('inf'):
                cost_display = "Infinity"
            else:
                cost_display = f"{cost_str:.2f}"
            
            row = [
                result["algorithm"],
                result["dataset"].capitalize(),
                str(result["nodes"]),
                f"{result['execution_time_ms']:.4f}",
                f"{result['memory_used_mb']:.4f}",
                cost_display
            ]
            table_data.append(row)
        
        table = ax.table(cellText=table_data, cellLoc="center", loc="center",
                        colWidths=[0.18, 0.15, 0.12, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header row
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor("#4ECDC4")
            table[(0, i)].set_text_props(weight="bold", color="white")
        
        # Alternate row colors
        for i in range(1, len(table_data)):
            color = "#F0F0F0" if i % 2 == 0 else "white"
            for j in range(len(table_data[0])):
                table[(i, j)].set_facecolor(color)
        
        plt.title("Performance Summary Table", fontsize=14, fontweight="bold", pad=20)
        plt.tight_layout()
        filepath = f"{self.output_dir}/summary_table.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def generate_all_charts(self):
        """Generate all available charts"""
        print("\nGenerating visualization charts...")
        print("-" * 60)
        
        self.chart_execution_time_comparison()
        self.chart_solution_quality_comparison()
        self.chart_memory_usage_comparison()
        self.chart_time_vs_quality_tradeoff()
        self.chart_complexity_analysis()
        self.chart_performance_summary_table()
        
        print("-" * 60)
        print(f"✓ All charts saved to: {self.output_dir}")
    
    def generate_report_html(self):
        """Generate an HTML report with all charts"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUDOS - Algorithm Performance Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        header h1 { font-size: 2.5em; margin-bottom: 10px; }
        header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        .section {
            margin-bottom: 50px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 40px;
        }
        .section:last-child { border-bottom: none; }
        .section h2 {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(800px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }
        .chart-container {
            background: #f9f9f9;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #ddd;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .chart-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 { font-size: 1.2em; margin-bottom: 10px; opacity: 0.9; }
        .stat-card .value { font-size: 2em; font-weight: bold; }
        footer {
            background: #f0f0f0;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            header h1 { font-size: 1.8em; }
            .chart-grid { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚚 SUDOS Performance Report</h1>
            <p>Smart Urban Delivery Optimization System - Algorithm Analysis</p>
        </header>
        
        <div class="content">
            <div class="section">
                <h2>📊 Execution Time Comparison</h2>
                <div class="chart-grid">
                    <div class="chart-container">
                        <img src="execution_time_comparison.png" alt="Execution Time Comparison">
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Solution Quality Analysis</h2>
                <div class="chart-grid">
                    <div class="chart-container">
                        <img src="solution_quality_comparison.png" alt="Solution Quality">
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>⚡ Performance Trade-offs</h2>
                <div class="chart-grid">
                    <div class="chart-container">
                        <img src="time_vs_quality_tradeoff.png" alt="Time vs Quality">
                    </div>
                    <div class="chart-container">
                        <img src="complexity_analysis.png" alt="Complexity Analysis">
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>💾 Resource Utilization</h2>
                <div class="chart-grid">
                    <div class="chart-container">
                        <img src="memory_usage_comparison.png" alt="Memory Usage">
                    </div>
                    <div class="chart-container">
                        <img src="summary_table.png" alt="Summary Table">
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Generated by SUDOS Analysis Module | Algorithm Performance Benchmarking</p>
        </footer>
    </div>
</body>
</html>
        """
        
        html_file = f"{self.output_dir}/report.html"
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML report saved: {html_file}")


if __name__ == "__main__":
    generator = ChartGenerator()
    generator.generate_all_charts()
    generator.generate_report_html()
    print("\n✓ Visualization complete! Open 'analysis/charts/report.html' to view the report.")
