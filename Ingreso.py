from Transaccion import Transaccion

class Ingreso(Transaccion):
    def __init__(self, concepto, importe, categoria, fecha, origen):
        super().__init__(concepto, importe, categoria, fecha)
        self.origen = origen

    def mostrar(self):
        return f'[INGRESO] {super().mostrar()} (Origen: {self.origen})'