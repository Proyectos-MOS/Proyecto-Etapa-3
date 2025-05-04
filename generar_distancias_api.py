import pandas as pd
import requests
import time

# === Cargar archivos
clients = pd.read_csv("data-caso1/clients.csv")
depots = pd.read_csv("data-caso1/depots.csv")

# === Coordenadas
nodes = {}
nodes[0] = (depots.loc[0, "Longitude"], depots.loc[0, "Latitude"])  # Depósito

for idx, row in clients.iterrows():
    node_id = int(row["ClientID"])
    coord = (row["Longitude"], row["Latitude"])
    nodes[node_id] = coord

# === Configuración de API
api_key = '5b3ce3597851110001cf6248be808c25e2964fb2b3e74f3c74d8ce63'
headers = {
    'Authorization': api_key,
    'Content-Type': 'application/json'
}
url = 'https://api.openrouteservice.org/v2/directions/driving-car'

# === Crear grafo (matriz de distancias y tiempos)
grafo = {}

for i, coords_i in nodes.items():
    grafo[i] = {}
    for j, coords_j in nodes.items():
        if i == j:
            grafo[i][j] = {
                "distance_km": 999.0,
                "time_min": 999.0
            }
            continue

        params = {
            'start': f"{coords_i[0]},{coords_i[1]}",
            'end': f"{coords_j[0]},{coords_j[1]}"
        }

        print(f"Calculando de {i} a {j}...")
        response = requests.get(url, headers=headers, params=params)
        time.sleep(1.1)  # Evitar bloqueo por rate-limit

        if response.status_code == 200:
            data = response.json()
            segmento = data['features'][0]['properties']['segments'][0]
            distancia = round(segmento['distance'] / 1000, 2)
            duracion = round(segmento['duration'] / 60, 2)
            grafo[i][j] = {
                "distance_km": distancia,
                "time_min": duracion
            }
        else:
            grafo[i][j] = {
                "distance_km": 999.0,
                "time_min": 999.0
            }
            print(f"Error {response.status_code} entre {i} y {j}")

print("✅ Grafo generado correctamente y guardado en variable.")
