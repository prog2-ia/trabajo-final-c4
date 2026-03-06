from Transaccion import Transaccion
class Gasto(Transaccion):
    def __init__(self, concepto, importe, categoria, fecha, metodo_pago):
        super().__init__(concepto, importe, categoria, fecha)
        self.metodo_pago = metodo_pago

    def mostrar(self):
        return f'[GASTO] {super().mostrar()} (Pagado con: {self.metodo_pago})'