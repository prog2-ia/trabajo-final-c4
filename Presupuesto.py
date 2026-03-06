class Presupuesto:
    def __init__(self, mes, cantidad):
        self.mes = mes
        self.cantidad = cantidad

    def sumar(self, otro):
        return self.cantidad + otro.cantidad

    def comparar(self, otro):
        return self.cantidad > otro.cantidad

    def mostrar(self):
        print(f'{self.mes}: {self.cantidad}')