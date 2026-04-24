from Gasto import Gasto

class GastoFijo(Gasto):
    def __init__(self, concepto, importe, categoria, fecha, metodo_pago, frecuencia="Mensual"):
        # Llamamos al constructor de Gasto
        super().__init__(concepto, importe, categoria, fecha, metodo_pago)
        self.frecuencia = frecuencia

    def mostrar(self):
        # Polimorfismo: modificamos el mensaje para indicar que es recurrente
        return f'[GASTO FIJO - {self.frecuencia}] {self.fecha} | {self.concepto}: {self.importe}€ ({self.metodo_pago})'