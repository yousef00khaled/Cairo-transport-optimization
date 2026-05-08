# 🚗 Cairo Transportation Management System

**CSE112 — Design and Analysis of Algorithms**
Alamein International University

---

## 🎯 Overview

A full-stack transportation management system for Greater Cairo that implements and visualizes multiple algorithmic approaches to optimize the city's transportation network.

### Algorithms Implemented

| Algorithm | Module | Purpose |
|---|---|---|
| **Kruskal's / Prim's MST** | Infrastructure | Optimal road network design |
| **Dijkstra's** | Traffic Flow | Shortest path routing |
| **A* Search** | Emergency | Hospital emergency routing |
| **Dynamic Programming** | Public Transit | Schedule & maintenance optimization |
| **Greedy** | Signal Control | Traffic signal timing |
| **Random Forest (ML)** | Prediction | Traffic congestion forecasting |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py

# 3. Open in browser
# http://localhost:5000
```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or with Docker directly
docker build -t cairo-transport .
docker run -p 5000:5000 cairo-transport
```

---

## 📁 Project Structure

```
├── app.py                     # Flask API server
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker containerization
├── docker-compose.yml         # Docker Compose config
│
├── data/
│   └── cairo_data.py          # All Cairo network data
│
├── core/
│   ├── graph.py               # Graph data structure
│   ├── mst.py                 # Kruskal's & Prim's MST
│   ├── shortest_path.py       # Dijkstra + Yen's k-shortest
│   ├── astar.py               # A* search + race comparison
│   ├── dynamic_programming.py # DP scheduling & knapsack
│   ├── greedy.py              # Signal optimization
│   └── traffic_simulation.py  # Traffic simulation
│
├── bonus/
│   └── ml_prediction.py       # scikit-learn traffic predictor
│
├── templates/
│   └── index.html             # Main web interface
│
└── static/
    ├── css/style.css           # Dark theme styles
    └── js/
        ├── app.js              # Main controller
        ├── map.js              # Leaflet map integration
        ├── algorithms.js       # Result displays
        ├── race.js             # Algorithm race animation
        └── charts.js           # Chart utilities
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/data` | Network data (nodes, edges) |
| POST | `/api/mst` | Compute MST |
| POST | `/api/shortest-path` | Dijkstra routing |
| POST | `/api/emergency-route` | A* emergency routing |
| POST | `/api/transit-optimize` | DP transit optimization |
| POST | `/api/signal-optimize` | Greedy signal optimization |
| POST | `/api/traffic-predict` | ML traffic prediction |
| POST | `/api/race` | Dijkstra vs A* race |
| POST | `/api/simulate` | Traffic simulation |

---

## 🎨 Features

- **Interactive Cairo Map** — Real OpenStreetMap with dark tiles
- **Algorithm Visualization** — Step-by-step execution
- **Algorithm Race** — Side-by-side Dijkstra vs A* animation
- **ML Predictions** — Random Forest congestion forecasting
- **Premium Dark UI** — Glassmorphism theme with animations
- **Docker Ready** — Containerized for any machine
