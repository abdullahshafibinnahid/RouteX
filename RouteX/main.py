from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import heapq

app = FastAPI(title="RouteX Dynamic Map Solver")

# CORS POLICY HANDLING
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EdgeData(BaseModel):
    from_node: str
    to_node: str
    weight: float

class MapGraphRequest(BaseModel):
    nodes: Dict[str, List[float]] 
    edges: List[EdgeData]          
    start: str
    end: str

def dijkstra_dynamic(nodes: dict, edges: list, start: str, end: str):
    graph = {node_id: [] for node_id in nodes}
    for edge in edges:
        graph[edge.from_node].append((edge.to_node, edge.weight))
        graph[edge.to_node].append((edge.from_node, edge.weight))
    
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    parent = {node: None for node in graph}

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_dist > distances[current_node]:
            continue
        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, []):
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                parent[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path = path[::-1]

    if distances[end] == float('infinity'):
        return [], float('infinity'), []
        
    path_coords = [nodes[node] for node in path]
    return path, distances[end], path_coords

@app.post("/calculate-dynamic-route")
def calculate_route(request: MapGraphRequest):
    if request.start not in request.nodes or request.end not in request.nodes:
        raise HTTPException(status_code=400, detail="Start or End node missing in the network.")
    
    path, distance, coords = dijkstra_dynamic(request.nodes, request.edges, request.start, request.end)
    return {
        "path": path,
        "distance": round(distance, 2),
        "coordinates": coords
    }

# home root
@app.get("/", response_class=HTMLResponse)
async def get_map_interface():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RouteX - Dynamic Map Builder</title>
        <!-- Leaflet.js Live Map CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            /* --- Global Reset & Styling --- */
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
            body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; min-height: 100vh; padding: 30px 15px; display: flex; justify-content: center; align-items: center; }
            
            /* --- Glassmorphism Container --- */
            .container { width: 100%; max-width: 1100px; background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 30px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); }
            h2 { font-size: 28px; font-weight: 700; background: linear-gradient(90deg, #38bdf8, #06b6d4); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
            p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; line-height: 1.5; }
            
            /* --- Toolbar controls --- */
            .controls { display: flex; gap: 12px; background: rgba(15, 23, 42, 0.6); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
            label { font-size: 13px; font-weight: 600; text-transform: uppercase; color: #38bdf8; margin-left: 8px; }
            select { background: #0f172a; color: #f8fafc; border: 1px solid #334155; padding: 10px 16px; font-size: 14px; border-radius: 8px; outline: none; cursor: pointer; min-width: 120px; }
            
            /* --- Premium Buttons --- */
            button { padding: 11px 20px; font-size: 14px; font-weight: 600; border-radius: 8px; border: none; cursor: pointer; transition: all 0.2s ease; }
            button:active { transform: scale(0.97); }
            .btn-mode { background: #334155; color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.05); }
            .btn-mode:hover { background: #475569; color: #f8fafc; }
            .btn-mode.active { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4); }
            #addEdgeBtn.active { background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4); }
            .btn-action { background: linear-gradient(135deg, #10b981 0%, #047857 100%); color: white; margin-left: auto; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); }
            .btn-action:hover { background: linear-gradient(135deg, #059669 0%, #065f46 100%); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6); }
            
            /* --- Map Design --- */
            #map { height: 500px; width: 100%; border-radius: 14px; border: 2px solid #334155; box-shadow: inset 0 0 20px rgba(0,0,0,0.4); z-index: 1; }
            .leaflet-layer, .leaflet-control-zoom-in, .leaflet-control-zoom-out { filter: invert(90%) hue-rotate(180deg) brightness(95%) contrast(90%); }
            
            /* --- Status Info --- */
            .info { font-size: 14px; font-weight: 500; color: #cbd5e1; margin-top: 20px; padding: 16px 20px; background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); border-left: 4px solid #38bdf8; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); line-height: 1.6; }
            
            @media (max-width: 768px) { .controls { flex-direction: column; align-items: stretch; } .btn-action { margin-left: 0; } }
        </style>
    </head>
    <body>
    <div class="container">
        <h2>RouteX: Build Your Own Map Network</h2>
        <p>Instructions: Click on the map to add custom stops. Switch to 'Link Stops' to build roads between them. Choose Start/End and calculate the shortest path.</p>
        <div class="controls">
            <button id="addNodeBtn" class="btn-mode active" onclick="setMode('addNode')">Mode: Add Stops</button>
            <button id="addEdgeBtn" class="btn-mode" onclick="setMode('addEdge')">Mode: Link Stops (Roads)</button>
            <label>Start:</label>
            <select id="startSelect"><option value="">-- Select --</option></select>
            <label>End:</label>
            <select id="endSelect"><option value="">-- Select --</option></select>
            <button class="btn-action" onclick="findCustomRoute()">Find Shortest Route</button>
            <button style="background: #ef4444; color: white;" onclick="clearMap()">Reset</button>
        </div>
        <div id="map"></div>
        <div class="info" id="statusInfo">Status: Ready. Click anywhere on the map to place stops.</div>
    </div>

    <!-- Leaflet.js Live Map Script -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const map = L.map('map').setView([23.7771, 90.3842], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);

        let nodes = {}, edges = [], nodeCount = 0, currentMode = 'addNode', firstSelectedNodeForEdge = null, activeRouteLine = null;

        // Haversine Formula
        function calculateDistance(lat1, lon1, lat2, lon2) {
            const R = 6371;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
            return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
        }

        function setMode(mode) {
            currentMode = mode;
            document.getElementById('addNodeBtn').classList.toggle('active', mode === 'addNode');
            document.getElementById('addEdgeBtn').classList.toggle('active', mode === 'addEdge');
            firstSelectedNodeForEdge = null;
            document.getElementById('statusInfo').innerText = mode === 'addNode' ? 
                "Status: Click anywhere on the map to add a stop." : 
                "Status: Click on a stop, then click another target stop to link them with a road.";
        }

        map.on('click', function(e) {
            if (currentMode !== 'addNode') return;
            const lat = e.latlng.lat, lng = e.latlng.lng, nodeId = `Stop_${nodeCount++}`;
            nodes[nodeId] = [lat, lng];
            document.getElementById('startSelect').add(new Option(nodeId, nodeId));
            document.getElementById('endSelect').add(new Option(nodeId, nodeId));

            const marker = L.circleMarker([lat, lng], { radius: 10, fillColor: "#38bdf8", color: "#fff", weight: 2, fillOpacity: 1 }).addTo(map).bindPopup(`<b>${nodeId}</b>`).openPopup();
            marker.on('click', function(event) {
                L.DomEvent.stopPropagation(event);
                if (currentMode === 'addEdge') handleEdgeCreation(nodeId);
            });
        });

        function handleEdgeCreation(nodeId) {
            if (!firstSelectedNodeForEdge) {
                firstSelectedNodeForEdge = nodeId;
                document.getElementById('statusInfo').innerText = `Linking from ${nodeId}. Now click another target stop!`;
            } else {
                if (firstSelectedNodeForEdge === nodeId) return;
                const from = firstSelectedNodeForEdge, to = nodeId;
                const dist = calculateDistance(nodes[from][0], nodes[from][1], nodes[to][0], nodes[to][1]);
                edges.push({ from_node: from, to_node: to, weight: dist });
                L.polyline([nodes[from], nodes[to]], { color: '#f59e0b', weight: 4, dashArray: '6, 6' }).addTo(map);
                document.getElementById('statusInfo').innerText = `Road built: ${from} ➜ ${to} (${dist.toFixed(2)} km)`;
                firstSelectedNodeForEdge = null;
            }
        }

        async function findCustomRoute() {
            const start = document.getElementById('startSelect').value, end = document.getElementById('endSelect').value;
            if (!start || !end) return alert("Select Start and End points!");
            try {
                const response = await fetch(`${window.location.origin}/calculate-dynamic-route`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nodes, edges, start, end })
                });
                const data = await response.json();
                if (response.ok) {
                    document.getElementById('statusInfo').innerHTML = `🏁 Route Solved!<br>🧭 Path: ${data.path.join(' ➜ ')}<br>📏 Distance: ${data.distance} km`;
                    if (activeRouteLine) map.removeLayer(activeRouteLine);
                    activeRouteLine = L.polyline(data.coordinates, { color: '#10b981', weight: 7 }).addTo(map);
                    map.fitBounds(activeRouteLine.getBounds());
                } else {
                    document.getElementById('statusInfo').innerText = `Error: ${data.detail}`;
                }
            } catch (e) {
                document.getElementById('statusInfo').innerText = "API Network Error! Check your FastAPI server.";
            }
        }

        function clearMap() { location.reload(); }
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)