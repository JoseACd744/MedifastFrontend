from flask import Blueprint, render_template, request
import requests
import pandas as pd
import osmnx as ox
import numpy as np
from scipy.spatial.distance import cdist
import networkx as nx

main_bp = Blueprint('main_bp', __name__)

def haversine(lat_lon1, lat_lon2):
    lat1, lon1 = lat_lon1
    lat2, lon2 = lat_lon2
    R = 6371.0  # Radio medio de la Tierra en kilómetros
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance

def obtener_datos_backend():
    response_hospitales = requests.get('https://rutasmedicamentos.azurewebsites.net/hospitals')
    hospitales_data = response_hospitales.json()

    response_almacenes = requests.get('https://rutasmedicamentos.azurewebsites.net/undergroundWarehouses')
    almacenes_data = response_almacenes.json()

    return hospitales_data, almacenes_data

def calcular_distancias_geograficas(hospitales, almacenes):
    distancias_hospitales = cdist(hospitales[['latitud', 'longitud']].values, hospitales[['latitud', 'longitud']].values, metric=haversine)
    distancias_almacen_hospital = cdist(almacenes[['latitud', 'longitud']].values, hospitales[['latitud', 'longitud']].values, metric=haversine)
    return distancias_hospitales, distancias_almacen_hospital

def calcular_ruta_osm(origen, destino):
    # Crear un grafo de la red de calles en el área relevante
    G = ox.graph_from_point((origen[0], origen[1]), dist=5000, network_type='drive')
    
    # Obtener los nodos más cercanos a los puntos de origen y destino
    origen_node = ox.distance.nearest_nodes(G, origen[1], origen[0])
    destino_node = ox.distance.nearest_nodes(G, destino[1], destino[0])
    
    # Calcular la ruta más corta
    ruta_nodes = nx.shortest_path(G, origen_node, destino_node, weight='length')
    ruta_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in ruta_nodes]
    
    return ruta_coords

def construir_grafo(distancias_hospitales):
    G = nx.Graph()
    num_hospitales = len(distancias_hospitales)
    for i in range(num_hospitales):
        for j in range(i + 1, num_hospitales):
            if distancias_hospitales[i][j] > 0:  # Solo agregar distancias mayores a 0
                G.add_edge(i+1, j+1, weight=distancias_hospitales[i][j])
    return G

def encontrar_mst(G):
    return nx.minimum_spanning_tree(G)

def seleccionar_ruta(T, inicio, destino, almacenes_df, hospitales_dict, distancias_almacen_hospital, hospitales_df):
    ruta_hospitales = list(nx.dijkstra_path(T, source=inicio, target=destino))
    ruta_limpia = []
    distancia_total = 0
    
    for i in range(len(ruta_hospitales) - 1):
        origen = ruta_hospitales[i] - 1
        destino = ruta_hospitales[i + 1] - 1
        distancia = T.edges[origen+1, destino+1]['weight']
        nombre = hospitales_df.iloc[destino]['name']
        if distancia > 0: 
            ruta_limpia.append((nombre, distancia))
            distancia_total += distancia
    
    ruta_str = f"Origen (Almacén {almacenes_df.iloc[inicio-1]['name']})"
    for nombre, distancia in ruta_limpia:
        ruta_str += f" ⎯⎯ ({distancia:.2f} km) 🡢 {nombre}"
    ruta_str += f"\nDistancia Total: {distancia_total:.2f} km"

    # Devuelve la ruta como cadena de texto
    return ruta_str

@main_bp.route('/')
def index():
    # Obtener la lista de hospitales y almacenes desde el backend
    hospitales_data, almacenes_data = obtener_datos_backend()

    return render_template('index.html', hospitals=hospitales_data, warehouses=almacenes_data)

@main_bp.route('/search', methods=['POST'])
def search():
    selected_warehouse = request.form['selected_warehouse']
    selected_hospital = request.form['selected_hospital']

    hospitales_data, almacenes_data = obtener_datos_backend()
    selected_warehouse_name = requests.get('https://rutasmedicamentos.azurewebsites.net/undergroundWarehouses/' + selected_warehouse).json().get('name')

    # Encontrar el índice del almacén seleccionado
    index_almacen = None
    for idx, almacen in enumerate(almacenes_data):
        if almacen['name'] == selected_warehouse_name:
            index_almacen = idx
            break

    if index_almacen is None:
        return render_template('error.html', message="El almacén seleccionado no está disponible.")

    lat_lon_almacen = (almacenes_data[index_almacen]['latitud'], almacenes_data[index_almacen]['longitud'])
    lat_lon_hospital = (hospitales_data[int(selected_hospital)]['latitud'], hospitales_data[int(selected_hospital)]['longitud'])

    # Calcular ruta utilizando OSM
    ruta = calcular_ruta_osm(lat_lon_almacen, lat_lon_hospital)

    # Calcular distancias geográficas
    distancias_hospitales, distancias_almacen_hospital = calcular_distancias_geograficas(pd.DataFrame(hospitales_data), pd.DataFrame(almacenes_data))

    # Construir grafo y encontrar MST
    G = construir_grafo(distancias_hospitales)
    T = encontrar_mst(G)

    # Seleccionar ruta óptima
    ruta_nombre = seleccionar_ruta(T, int(selected_warehouse), int(selected_hospital), pd.DataFrame(almacenes_data), {hospital['id']: hospital['name'] for hospital in hospitales_data}, distancias_almacen_hospital, pd.DataFrame(hospitales_data))

    selected_warehouse_info = almacenes_data[index_almacen]
    selected_hospital_info = hospitales_data[int(selected_hospital) - 1]

    #muestra la ruta
    print(ruta_nombre)

    return render_template('result.html', selected_warehouse=selected_warehouse_info, selected_hospital=selected_hospital_info, ruta=ruta, coordenadas_ruta=ruta, ruta_nombre = ruta_nombre)
