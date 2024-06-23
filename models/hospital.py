# models/hospital.py
class Hospital:
    def __init__(self, name, id, latitud, direccion, categoria, longitud, distrito, telefono):
        self.name = name
        self.id = id
        self.latitud = latitud
        self.direccion = direccion
        self.categoria = categoria
        self.longitud = longitud
        self.distrito = distrito
        self.telefono = telefono
