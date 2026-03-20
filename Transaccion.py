from abc import ABC, abstractmethod

class Transaccion(ABC):
    def __init__(self, concepto, importe, categoria, fecha):
        self.concepto = concepto
        self.importe = importe
        self.categoria = categoria
        self.fecha = fecha

    @property
    def importe(self):
        return self.__importe

    @importe.setter
    def importe(self, valor):
        if valor <= 0:
            raise ValueError("El importe debe ser estrictamente mayor que 0.")
        self.__importe = valor

    @property
    def concepto(self):
        return self.__concepto

    @concepto.setter
    def concepto(self, valor):
        self.__concepto = valor

    @property
    def categoria(self):
        return self.__categoria

    @categoria.setter
    def categoria(self, valor):
        self.__categoria = valor

    @property
    def fecha(self):
        return self.__fecha

    @fecha.setter
    def fecha(self, valor):
        self.__fecha = valor

    @abstractmethod
    def mostrar(self):

        return f'[{self.fecha}] {self.concepto}: {self.importe}'