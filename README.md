---

# 🚚 SUDOS – Smart Urban Delivery Optimization System

SUDOS is a **Design and Analysis of Algorithms (DAA)** project that simulates how modern delivery platforms optimize delivery routes in urban environments. The system models a city as a **graph**, where nodes represent locations and edges represent distances. Using this model, the project computes efficient delivery routes for multiple agents while minimizing travel time and cost.

Inspired by real-world logistics systems such as **Amazon, Swiggy, and Blinkit**, SUDOS explores how classical algorithms can be applied to real-world routing problems and evaluates the trade-offs between optimal and heuristic solutions.

---

## 🎯 Objectives

* Model an urban delivery network using **graph data structures**
* Assign delivery requests to multiple delivery agents
* Compute efficient delivery routes
* Implement and compare multiple **algorithmic paradigms**
* Analyze **time complexity, scalability, and performance**

---

## ⚙️ Algorithms Implemented

| Algorithm Paradigm  | Algorithm            | Purpose                             |
| ------------------- | -------------------- | ----------------------------------- |
| Greedy              | Nearest Neighbor     | Fast baseline route generation      |
| Graph               | Dijkstra’s Algorithm | Shortest path computation           |
| Dynamic Programming | Bitmask TSP          | Optimal routing for small datasets  |
| Approximation       | Heuristic TSP        | Efficient routing for larger graphs |

These algorithms allow us to compare **exact solutions vs heuristic approaches** for delivery optimization.

---

## 🧠 System Workflow

1. Model the city as a **weighted graph**
2. Generate or load delivery request datasets
3. Compute shortest paths between locations
4. Apply routing algorithms to generate delivery routes
5. Compare results based on **cost, runtime, and scalability**

---

## 📁 Project Structure

```
SUDOS
│
├── algorithms
│   ├── dijkstra.py
│   ├── greedy_tsp.py
│   ├── dp_tsp.py
│   └── heuristic_tsp.py
│
├── core
│   └── graph.py
│
├── datasets
│   └── [JSON Datasets]
│
├── docs
│   └── PROJECT_DOCUMENTATION.md
│
├── analysis
│   ├── analysis_runner.py
│   ├── benchmark.py
│   └── charts.py
│
├── tests             
│   └── test_system.py
│
├── tools             
│   └── generate_datasets.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## 👥 Team Members

* **Shreeyanshi Padhy**
* **Abha Kiran Dongre**
* **Ananya Alfred**
* **Lavanya R**

---

## 📊 Expected Outcome

This project demonstrates how algorithmic paradigms such as **Greedy methods, Graph algorithms, and Dynamic Programming** can be applied to optimize real-world delivery systems. The study highlights the balance between **optimal solutions and computational efficiency** in urban logistics.

---

## 🚀 Setup Instructions

To run SUDOS locally, set up your Python environment and install the dependencies.

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

For more detailed information, please read the [Project Documentation](docs/PROJECT_DOCUMENTATION.md).
