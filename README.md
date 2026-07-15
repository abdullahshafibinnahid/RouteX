# 📍 RouteX: Dynamic Map Network Builder & Solver

RouteX is an interactive, real-time web application that allows users to dynamically design a spatial network (graph) on a live map, link nodes with auto-calculated distances, and compute the shortest path using **Dijkstra's Algorithm**. 

Built entirely in a single-file python backend using **FastAPI** and an interactive **Leaflet.js** frontend.

---

## ✨ Features
*   **Dynamic Node Placement:** Click anywhere on the map to drop custom stops (nodes).
*   **Custom Road Network:** Link stops in real-time. The application automatically calculates the geographical weight (distance in km) between them using the **Haversine Formula**.
*   **Fast Shortest Path Computation:** Leverages a highly-optimized priority-queue-based Dijkstra's Algorithm (`heapq` in Python) to solve routes instantly.
*   **Fully Responsive Dashboard:** A premium glassmorphism dark-themed UI that works on both desktop and mobile devices.
*   **Zero-Config Setup:** Served entirely from a single Python file to eliminate CORS or local file system routing issues.

---

## 🛠️ Tech Stack
*   **Backend:** Python 3.10+, FastAPI, Uvicorn
*   **Frontend:** HTML5, CSS3 (Glassmorphism design), Vanilla JavaScript, Leaflet.js (for map rendering)
*   **Algorithm:** Dijkstra's Shortest Path Algorithm

---

## 🚀 Getting Started & Running the App

Make sure you have Python installed, then run this single sequence of commands in your terminal to set up and start the application:

```bash
# Install the required dependencies
pip install fastapi uvicorn pydantic

# Clone the repository
git clone https://github.com/YOUR_USERNAME/routex-map-solver.git

# Navigate to the project directory
cd routex-map-solver

# Run the single-file server
python main.py
```
After running the server, open your browser and navigate to:
`http://127.0.0.1:8000/`

---

## 🧭 How to Use

* **Add Stops:** While in **Mode: Add Stops,** click anywhere on the map to place nodes (`Stop_0`, `Stop_1`, etc.).
* **Build Roads:** Click on **Mode: Link Stops (Roads).** Click a starting node, then click a target node to connect them with a road.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
