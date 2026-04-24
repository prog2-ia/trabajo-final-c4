from Ingreso import Ingreso

class IngresoFijo(Ingreso):
    def __init__(self, concepto, importe, categoria, fecha, origen, frecuencia="Mensual"):
        # Hereda de Ingreso
        super().__init__(concepto, importe, categoria, fecha, origen)
        self.frecuencia = frecuencia

    def mostrar(self):
        # Polimorfismo para identificar ingresos recurrentes
        return f'[INGRESO FIJO - {self.frecuencia}] {self.fecha} | {self.concepto}: {self.importe}€ (Origen: {self.origen})'