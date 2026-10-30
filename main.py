# Software FJ - Fase 4 - 213023 UNAD 
from abc import ABC, abstractmethod
from datetime import datetime

LOGS = []
def registrar_log(mensaje, nivel="INFO"):
    texto = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{nivel}] {mensaje}"
    LOGS.append(texto)

class DatosInvalidosError(Exception): pass
class ServicioNoDisponibleError(Exception): pass
class ReservaInvalidaError(Exception): pass
class OperacionNoPermitidaError(Exception): pass

class EntidadGeneral(ABC):
    def __init__(self, id_entidad):
        self._id = id_entidad
        self._fecha = datetime.now()
    def validar(self): pass

class Cliente(EntidadGeneral):
    def __init__(self, id_entidad, nombre, email, telefono, documento):
        super().__init__(id_entidad)
        self._nombre=nombre; self._email=email; self._telefono=telefono; self._documento=documento
        if len(nombre)<3: raise DatosInvalidosError("Nombre invalido")
        if "@" not in email: raise DatosInvalidosError(f"Email invalido {email}")
    @property
    def nombre(self): return self._nombre

class ReservaSala(EntidadGeneral):
    def __init__(self, id, nombre, precio, capacidad, horas, proyector=False):
        super().__init__(id)
        self._nombre=nombre; self._precio_base=precio; self.capacidad=capacidad; self.horas=horas; self.proyector=proyector; self._disponible=True
        if capacidad<=0: raise DatosInvalidosError("Capacidad 0")
        if horas<=0: raise ReservaInvalidaError("Horas 0")
    def calcular_costo(self, dias=1):
        extra=20000 if self.proyector else 0
        return (self._precio_base*self.horas+extra)*dias
    def describir_servicio(self): return f"SALA {self._nombre} Cap {self.capacidad}"

class AlquilerEquipo(EntidadGeneral):
    def __init__(self, id, nombre, precio, tipo, cantidad, dias):
        super().__init__(id)
        self._nombre=nombre; self._precio_base=precio; self.tipo=tipo; self.cantidad=cantidad; self.dias=dias; self._disponible=True
        if tipo not in ["laptop","proyector","sonido","video"]: raise ServicioNoDisponibleError(f"Tipo {tipo} no disponible")
    def calcular_costo(self, dias=None):
        d=dias if dias else self.dias
        return self._precio_base*self.cantidad*d
    def describir_servicio(self): return f"EQUIPO {self._nombre} Tipo {self.tipo}"

class AsesoriaEspecializada(EntidadGeneral):
    def __init__(self, id, nombre, precio, especialidad, horas, nivel="basico"):
        super().__init__(id)
        self._nombre=nombre; self._precio_base=precio; self.especialidad=especialidad; self.horas=horas; self.nivel=nivel; self._disponible=True
    def calcular_costo(self, dias=1):
        mult={"basico":1,"intermedio":1.5,"avanzado":2.2}
        return self._precio_base*self.horas*mult[self.nivel]*dias
    def describir_servicio(self): return f"ASESORIA {self._nombre} {self.nivel}"

class Reserva(EntidadGeneral):
    def __init__(self, id, cliente, servicio, duracion=1):
        super().__init__(id)
        self.cliente=cliente; self.servicio=servicio; self.duracion=duracion; self.estado="pendiente"
        if not servicio._disponible: raise ServicioNoDisponibleError("Servicio no disponible")
        if duracion<=0: raise ReservaInvalidaError("Duracion >0")
    def confirmar(self):
        if self.estado=="confirmada": raise OperacionNoPermitidaError("Ya confirmada")
        if self.estado=="cancelada": raise OperacionNoPermitidaError("No confirmar cancelada")
        self.estado="confirmada"
        registrar_log(f"Reserva {self._id} confirmada")
        print(f"[Reserva {self._id}] Estado {self.estado}")
    def cancelar(self):
        if self.estado=="cancelada": raise OperacionNoPermitidaError("Ya cancelada")
        self.estado="cancelada"
        registrar_log(f"Reserva {self._id} cancelada")
    def procesar(self):
        costo=self.servicio.calcular_costo(dias=self.duracion)
        registrar_log(f"Reserva {self._id} Costo {costo}")
        return costo
    def __str__(self): return f"Reserva[{self._id}] {self.cliente.nombre} -> {self.servicio._nombre}"

def main():
    LOGS.clear()
    print("=== INICIO 11 OPERACIONES SOFTWARE FJ ===\n")
    c1=Cliente(1,"Juan Perez","juan@email.com","3001234567","10123")
    print("1. OK Cliente", c1.nombre)
    try:
        Cliente(2,"Ana","ana.email.com","300","10123")
    except DatosInvalidosError as e:
        print(f"2. CAPTURADO Cliente invalido {e}")
    finally:
        print("   Finally 2 OK\n")
    s1=ReservaSala(1,"Sala Ejecutiva",50000,20,4,True)
    print(f"3. OK Sala {s1.describir_servicio()} Costo {s1.calcular_costo()}")
    try:
        ReservaSala(2,"Sala Mala",40000,0,2)
    except DatosInvalidosError as e:
        print(f"4. CAPTURADO Sala invalida {e}")
    s2=AlquilerEquipo(3,"Pack Laptops",30000,"laptop",5,3)
    print(f"5. OK Equipo {s2.describir_servicio()} Costo {s2.calcular_costo()}")
    try:
        AlquilerEquipo(4,"Drones",50000,"dron",2,1)
    except ServicioNoDisponibleError as e:
        print(f"6. CAPTURADO Equipo no disponible {e}")
    s3=AsesoriaEspecializada(5,"Asesoria Python",40000,"Desarrollo",10,"avanzado")
    print(f"7. OK Asesoria {s3.describir_servicio()} Costo {s3.calcular_costo()}")
    r1=Reserva(1,c1,s1,2)
    costo=r1.procesar(); r1.confirmar()
    print(f"8. OK Reserva Costo {costo}")
    try:
        s1._disponible=False
        Reserva(2,c1,s1,1)
    except ServicioNoDisponibleError as e:
        print(f"9. CAPTURADO Reserva no disponible {e}")
        s1._disponible=True
    try:
        print("\n10. Probando encadenamiento")
        Reserva(3,c1,s2,-5)
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
    for l in LOGS: print(l)

if __name__=="__main__": main()