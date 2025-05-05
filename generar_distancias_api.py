import pandas as pd
import requests
import time
import pprint
import json

# === Cargar archivos
clients = pd.read_csv("data-caso1/clients.csv")
depots  = pd.read_csv("data-caso1/depots.csv")

# === Coordenadas
nodes = {
    0: (
        depots.loc[0, "Longitude"],
        depots.loc[0, "Latitude"]
    )
}
for _, row in clients.iterrows():
    node_id = int(row["ClientID"])
    coord   = (row["Longitude"], row["Latitude"])
    nodes[node_id] = coord

# === Configuración de API
api_key = '5b3ce3597851110001cf6248f4bace05742cd52a0f6b877ce5d52bffe229f05a5f3132ac87cef6d3'
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
            # Sin desplazamiento: valor "infinito"
            grafo[i][j] = (999.0, 999.0)
            continue

        params = {
            'start': f"{coords_i[0]},{coords_i[1]}",
            'end':   f"{coords_j[0]},{coords_j[1]}"
        }

        print(f"Calculando de {i} a {j}…")
        response = requests.get(url, headers=headers, params=params)
        time.sleep(1.6)  # para no sobrepasar el rate-limit

        if response.status_code == 200:
            seg   = response.json()['features'][0]['properties']['segments'][0]
            dist  = round(seg['distance'] / 1000, 2)
            tiem  = round(seg['duration'] / 60, 2)
            # reemplazar 0.0 por "infinito"
            if dist == 0.0: dist = 999.0
            if tiem == 0.0: tiem = 999.0
            grafo[i][j] = (dist, tiem)

        elif response.status_code == 404:
            # ruta no encontrada
            grafo[i][j] = (999.0, 999.0)

        else:
            # otros errores HTTP
            print(f"Error {response.status_code}: {response.text}")
            grafo[i][j] = (999.0, 999.0)

# === Mostrar resultado
print("✅ Grafo generado correctamente:")
pprint.pprint(grafo, width=60)

# === Guardar en JSON
with open("distancias-tiempo-api-carro-3.json", "w") as f:
    json.dump(grafo, f, indent=2)

print("✅ Grafo guardado en 'distancias-tiempo-api-carro-1.json'")
