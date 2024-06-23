from flask import Blueprint, render_template, request
import requests
import pandas as pd
import osmnx as ox
import networkx as nx

main_bp = Blueprint('main_bp', __name__)

def obtener_datos_backend():
    response_hospitales = requests.get('https://rutasmedicamentos.azurewebsites.net/hospitals')
    hospitales_data = response_hospitales.json()

    response_almacenes = requests.get('https://rutasmedicamentos.azurewebsites.net/undergroundWarehouses')
    almacenes_data = response_almacenes.json()

    return hospitales_data, almacenes_data

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

@main_bp.route('/')
def index():
    # Obtener la lista de hospitales y almacenes desde el backend
    hospitales_data, almacenes_data = obtener_datos_backend()

    return render_template('index.html', hospitals=hospitales_data, warehouses=almacenes_data)

@main_bp.route('/search', methods=['POST'])
def search():
    selected_warehouse = request.form['selected_warehouse']
    selected_hospital = request.form['selected_hospital']

    print(f"Almacén seleccionado: {selected_warehouse}")
    print(f"Hospital seleccionado: {selected_hospital}")

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

    selected_warehouse = almacenes_data[index_almacen].get('name')
    selected_hospital = hospitales_data[int(selected_hospital) - 1].get('name')

    return render_template('result.html', selected_warehouse=selected_warehouse, selected_hospital=selected_hospital, ruta=ruta, coordenadas_ruta=ruta)
