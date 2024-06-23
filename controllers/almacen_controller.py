# controllers/warehouse_controller.py
from flask import Blueprint, jsonify
from models.almacen import UndergroundWarehouse
import requests  # Importa la biblioteca requests para realizar solicitudes HTTP al backend

warehouse_controller_bp = Blueprint('warehouse_controller_bp', __name__)

@warehouse_controller_bp.route('/warehouses', methods=['GET'])
def get_warehouses():
    # Realiza una solicitud GET al endpoint correspondiente en tu backend para obtener los datos de los almacenes
    response = requests.get('https://rutasmedicamentos.azurewebsites.net/undergroundWarehouses')  # Cambia la URL según tu backend
    if response.status_code == 200:
        warehouses_data = response.json()
        warehouses = [UndergroundWarehouse(**data) for data in warehouses_data]
        return jsonify([warehouse.__dict__ for warehouse in warehouses])
    else:
        return jsonify([])  # Devuelve una lista vacía en caso de error o si no hay datos

class WarehouseController:
    def get_warehouses(self):
        response = requests.get('https://rutasmedicamentos.azurewebsites.net/undergroundWarehouses')  # Cambia la URL según tu backend
        if response.status_code == 200:
            warehouses_data = response.json()
            warehouses = [UndergroundWarehouse(**data) for data in warehouses_data]
            return warehouses
        else:
            return []  # Devuelve una lista vacía en caso de error o si no hay datos
