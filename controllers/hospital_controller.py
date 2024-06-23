# controllers/hospital_controller.py
from flask import Blueprint, jsonify
from models.hospital import Hospital
import requests  # Importa la biblioteca requests para realizar solicitudes HTTP al backend

hospital_controller_bp = Blueprint('hospital_controller_bp', __name__)

@hospital_controller_bp.route('/hospitals', methods=['GET'])
def get_hospitals():
    # Realiza una solicitud GET al endpoint correspondiente en tu backend para obtener los datos de los hospitales
    response = requests.get('https://rutasmedicamentos.azurewebsites.net/hospitals')  # Cambia la URL según tu backend
    if response.status_code == 200:
        hospitals_data = response.json()
        hospitals = [Hospital(**data) for data in hospitals_data]
        return jsonify([hospital.__dict__ for hospital in hospitals])
    else:
        return jsonify([])  # Devuelve una lista vacía en caso de error o si no hay datos

class HospitalController:
    def get_hospitals(self):
        response = requests.get('https://rutasmedicamentos.azurewebsites.net/hospitals')  # Cambia la URL según tu backend
        if response.status_code == 200:
            hospitals_data = response.json()
            hospitals = [Hospital(**data) for data in hospitals_data]
            return hospitals
        else:
            return []  # Devuelve una lista vacía en caso de error o si no hay datos
