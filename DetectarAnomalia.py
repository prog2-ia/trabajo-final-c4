from Gasto import Gasto


class DetectorAnomalias:
    """
    Detecta gastos inusualmente altos comparando cada transacción
    con la media de los N gastos anteriores multiplicada por un factor.
    """

    def __init__(self, multiplicador=1.5, num_recientes=5):
        """
        :param multiplicador: Factor sobre la media que define el umbral (default 1.5).
        :param num_recientes: Número de gastos recientes usados para calcular la media.
        :raises ValueError: Si los parámetros son inválidos.
        """
        if multiplicador <= 0:
            raise ValueError(f"El multiplicador debe ser mayor que 0. Recibido: {multiplicador}")
        if num_recientes < 1:
            raise ValueError(f"num_recientes debe ser al menos 1. Recibido: {num_recientes}")

        self.multiplicador = multiplicador
        self.num_recientes = num_recientes

    def calcular_umbral_dinamico(self, lista_transacciones):
        """
        Calcula el umbral basado en la media de los últimos N gastos.

        :returns: Umbral calculado, o 0.0 si no hay gastos suficientes.
        """
        if not lista_transacciones:
            return 0.0

        gastos = [t.importe for t in lista_transacciones if isinstance(t, Gasto)]
        if not gastos:
            return 0.0

        ultimos = gastos[-self.num_recientes:]
        media = sum(ultimos) / len(ultimos)
        return media * self.multiplicador

    def escanear_transacciones(self, lista_transacciones):
        """
        Revisa todas las transacciones y genera alertas para gastos anómalos.

        :returns: Lista de strings con las alertas encontradas.
        """
        if not lista_transacciones:
            return ["No hay transacciones para analizar."]

        umbral = self.calcular_umbral_dinamico(lista_transacciones)
        if umbral == 0.0:
            return ["No hay suficientes gastos para calcular anomalías aún."]

        alertas = []
        for t in lista_transacciones:
            if isinstance(t, Gasto) and t.importe > umbral:
                exceso = t.importe - umbral
                alertas.append(
                    f"⚠  ALERTA: '{t.concepto}' → {t.importe:.2f}€  "
                    f"(umbral: {umbral:.2f}€, exceso: +{exceso:.2f}€)"
                )

        if not alertas:
            alertas.append(f"✔  Sin anomalías detectadas. Umbral actual: {umbral:.2f}€")

        return alertas

    def informe_anomalias(self, lista_transacciones):
        """
        Imprime un informe completo de anomalías detectadas.
        """
        alertas = self.escanear_transacciones(lista_transacciones)
        umbral = self.calcular_umbral_dinamico(lista_transacciones)

        print(f"\n{'─'*45}")
        print(f"  DETECTOR DE ANOMALÍAS")
        print(f"  Multiplicador: x{self.multiplicador} | Muestra: últimos {self.num_recientes} gastos")
        if umbral > 0:
            print(f"  Umbral actual: {umbral:.2f}€")
        print(f"{'─'*45}")
        for alerta in alertas:
            print(f"  {alerta}")
        print(f"{'─'*45}")

    def __repr__(self):
        return f"DetectorAnomalias(multiplicador={self.multiplicador}, num_recientes={self.num_recientes})"
