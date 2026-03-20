from Gasto import Gasto

class DetectorAnomalias:
    def __init__(self, multiplicador=1.5, num_recientes=3):
        # multiplicador: cuánto por encima de la media es una anomalía (1.5 = 50% más)
        # num_recientes: cuántos de los últimos gastos usamos para calcular la media
        self.multiplicador = multiplicador
        self.num_recientes = num_recientes

    def calcular_umbral_dinamico(self, lista_transacciones):
        """Calcula la media de los últimos gastos y devuelve el umbral."""
        # Filtramos la lista para sacar solo los importes de los objetos Gasto
        gastos = [t.importe for t in lista_transacciones if isinstance(t, Gasto)]

        if not gastos:
            return 0  # Si aún no hay gastos, devolvemos 0

        # Nos quedamos solo con los últimos 'num_recientes'
        ultimos_gastos = gastos[-self.num_recientes:]

        # Calculamos la media matemática
        media = sum(ultimos_gastos) / len(ultimos_gastos)

        # El umbral es la media multiplicada por nuestro margen
        return media * self.multiplicador

    def escanear_transacciones(self, lista_transacciones):
        """Revisa la lista de transacciones usando la media histórica."""
        alertas = []
        umbral = self.calcular_umbral_dinamico(lista_transacciones)

        if umbral == 0:
            return ["No hay suficientes gastos para calcular anomalías aún."]

        for transaccion in lista_transacciones:
            if isinstance(transaccion, Gasto):

                if transaccion.importe > umbral:
                    alertas.append(
                        f"ALERTA: Gasto inusualmente alto -> {transaccion.mostrar()} "
                        f"(El umbral actual es de {umbral:.2f}€)"
                    )

        return alertas