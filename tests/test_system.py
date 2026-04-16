import pytest
from pathlib import Path

def test_imports():
    """Test that all algorithms components can be imported properly"""
    try:
        from analysis.benchmark import Benchmark, BenchmarkMetrics
        from analysis.charts import ChartGenerator
        from analysis.analysis_runner import AnalysisRunner
        from algorithms.greedy_tsp import greedy_tsp
        from algorithms.dp_tsp import dp_tsp
        from core.graph import create_small_graph, generate_medium_graph
    except ImportError as e:
        pytest.fail(f"Failed to import a module: {e}")

def test_required_directories_exist():
    """Test that architectural directories exist"""
    required_dirs = [
        'analysis',
        'algorithms',
        'core',
        'datasets',
    ]
    for directory in required_dirs:
        assert Path(directory).exists(), f"Directory {directory} is missing"

def test_datasets_generation():
    """Test graph generation mechanics directly"""
    from core.graph import create_small_graph, generate_medium_graph
    
    small_g, small_c = create_small_graph()
    assert len(small_g) > 0, "Small graph missing nodes"
    
    med_g, med_c = generate_medium_graph(50)
    assert len(med_g) == 50, "Medium graph should have exactly 50 nodes"
