"""
TRABAJO UNAD GRUPAL - POO y Manejo de Excepciones
Grupo: TRABAJ-UNAD-GRUPAL-
Repositorio: maurixio1004773-code/TRABAJ-UNAD-GRUPAL-

Integrantes y aportes:
- Mauricio - maurixio1004773-code - Clase base Servicio y estructura main
- Ingrid Alejandra Muñoz Ruiz- ingridalejandra407-lgtm - Clase ReservaSala
- Yenifer Juliana Burbano Burbano - Julianaburbano65-lang - Clase AlquilerEquipo
- Jhesir Ruiz - jhesiruiz730-spec - Clase AsesoriaEspecializada y logs

Curso: Programacion Orientada a Objetos UNAD 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime

REGISTROS = []
LOGS = REGISTROS

def registrar_log(mensaje, nivel="INFO"):
    texto = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {nivel}: {mensaje}"
    REGISTROS.append(texto)

# --- Excepciones ---
class DatosInvalidosError(Exception): pass
class ServicioNoDisponibleError(Exception): pass
class ReservaInvalidaError(Exception): pass
class OperacionNoPermitidaError(Exception): pass

# --- Clase abstracta ---
class Servicio(ABC):
    def __init__(self, id_serv, nombre, precio_base):
        if precio_base <= 0:
            raise DatosInvalidosError(f"Precio invalido: {precio_base}")
        if not nombre:
            raise DatosInvalidosError("Nombre vacio")
        self.id = id_serv
        self.nombre = nombre
        self.precio_base = precio_base
        self._disponible = True

    @abstractmethod
    def describir_servicio(self): pass
    @abstractmethod
    def calcular_costo(self): pass

class ReservaSala(Servicio):
    def __init__(self, id_serv, nombre, precio_base, capacidad, horas):
        super().__init__(id_serv, nombre, precio_base)
        if capacidad <= 0 or horas <= 0:
            raise DatosInvalidosError(f"Capacidad u horas invalidas")
        self.capacidad = capacidad
        self.horas = horas
    def describir_servicio(self):
        return f"ReservaSala {self.nombre} cap {self.capacidad}"
    def calcular_costo(self):
        return self.precio_base * self.horas

class AlquilerEquipo(Servicio):
    def __init__(self, id_serv, nombre, precio_base, tipo_equipo, cantidad, dias):
        super().__init__(id_serv, nombre, precio_base)
        if cantidad <=0 or dias <=0:
            raise DatosInvalidosError("Cantidad o dias invalidos")
        self.tipo_equipo = tipo_equipo
        self.cantidad = cantidad
        self.dias = dias
    def describir_servicio(self):
        return f"AlquilerEquipo {self.nombre} ({self.tipo_equipo}) x{self.cantidad}"
    def calcular_costo(self):
        return self.precio_base * self.cantidad * self.dias

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_serv, nombre, precio_base, area, horas, nivel):
        super().__init__(id_serv, nombre, precio_base)
        if horas <=0:
            raise DatosInvalidosError("Horas invalidas")
        self.area = area
        self.horas = horas
        self.nivel = nivel
    def describir_servicio(self):
        return f"Asesoria {self.nombre} area {self.area} nivel {self.nivel}"
    def calcular_costo(self):
        factor = 1.5 if self.nivel.lower() == "avanzado" else 1.0
        return self.precio_base * self.horas * factor

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, duracion):
        if duracion <=0:
            raise ReservaInvalidaError(f"Duracion invalida: {duracion}")
        self.id = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "pendiente"
        registrar_log(f"Reserva {self.id} creada")
    def procesar(self):
        if not self.servicio._disponible:
            raise ServicioNoDisponibleError(f"Servicio {self.servicio.nombre} no disponible")
        costo = self.servicio.calcular_costo()
        registrar_log(f"Reserva {self.id} procesada costo {costo}")
        return costo
    def confirmar(self):
        if self.estado == "cancelada":
            raise OperacionNoPermitidaError(f"No se puede confirmar reserva cancelada {self.id}")
        self.estado = "confirmada"
        registrar_log(f"Reserva {self.id} confirmada")
    def cancelar(self):
        self.estado = "cancelada"
        registrar_log(f"Reserva {self.id} cancelada")
    def __str__(self):
        return f"Reserva {self.id} - {self.cliente} - {self.estado}"

def main():
    print("--- INICIO PRUEBAS UNAD ---")
    s1 = ReservaSala(1, "Sala Principal", 50000, 20, 2)
    print(f"1. OK Sala {s1.describir_servicio()} Costo {s1.calcular_costo()}")
    try:
        ReservaSala(2, "Sala Mala", 40000, 0, 2)
    except DatosInvalidosError as e:
        print(f"4. CAPTURADO Sala invalida {e}")
    s2 = AlquilerEquipo(3, "Pack Laptops", 30000, "laptop", 5, 3)
    print(f"5. OK Equipo {s2.describir_servicio()} Costo {s2.calcular_costo()}")
    try:
        AlquilerEquipo(4, "Drones", 50000, "dron", 2, 1)
        print(f"6. OK Drones permitido para prueba")
    except ServicioNoDisponibleError as e:
        print(f"6. CAPTURADO Equipo no disponible {e}")
    s3 = AsesoriaEspecializada(5, "Asesoria Python", 40000, "Desarrollo", 10, "avanzado")
    print(f"7. OK Asesoria {s3.describir_servicio()} Costo {s3.calcular_costo()}")
    r1 = Reserva(1, "c1", s1, 2)
    costo = r1.procesar()
    r1.confirmar()
    print(f"8. OK Reserva Costo {costo}")
    try:
        s1._disponible = False
        r_temp = Reserva(2, "c1", s1, 1)
        r_temp.procesar()
    except ServicioNoDisponibleError as e:
        print(f"9. CAPTURADO Reserva no disponible {e}")
    s1._disponible = True
    try:
        print("\n10. Probando encadenamiento")
        Reserva(3, "c1", s2, -5)
    except ReservaInvalidaError as e:
        print(f"10. CAPTURADO Duracion invalida {e}")
        try:
            raise OperacionNoPermitidaError("No permitida") from e
        except OperacionNoPermitidaError as ch:
            print(f"   Encadenada {ch} causa {ch.__cause__}")
    finally:
        print("10. Finally OK\n")
    try:
        r1.cancelar()
        print(f"11. OK Cancelacion {r1}")
        r1.confirmar()
    except OperacionNoPermitidaError as e:
        print(f"11. CAPTURADO No confirmar cancelada {e}")
    print("\n--- LOGS ---")
    for l in LOGS:
        print(l)

if __name__ == "__main__":
    main()
