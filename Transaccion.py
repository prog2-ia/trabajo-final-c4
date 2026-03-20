from abc import ABC, abstractmethod

class Transaccion(ABC):
    def __init__(self, concepto, importe, categoria, fecha):
        if importe <= 0:
            raise ValueError("El importe debe ser estrictamente mayor que 0.")

        self.concepto = concepto
        self.importe = importe
        self.categoria = categoria
        self.fecha = fecha

    @abstractmethod
    def mostrar(self):
        return f'[{self.fecha}] {self.concepto}: {self.importe}'