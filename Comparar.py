from datetime import datetime
from Gasto import Gasto


class Comparador:
    """
    Analiza la evolución de gastos mes a mes para una cuenta dada.
    """

    def __init__(self, cuenta):
        if cuenta is None:
            raise ValueError("Se necesita una cuenta válida para el comparador.")
        self.cuenta = cuenta

    def obtener_gastos_por_mes(self):
        """
        Agrupa los gastos por mes (clave "MM/YYYY") y devuelve un dict ordenado.

        :raises ValueError: Si no hay gastos registrados.
        """
        gastos_mensuales = {}

        for t in self.cuenta.transacciones:
            if isinstance(t, Gasto):
                try:
                    partes = t.fecha.split('/')
                    if len(partes) == 3:
                        clave = f"{partes[1]}/{partes[2]}"
                        gastos_mensuales[clave] = gastos_mensuales.get(clave, 0) + t.importe
                except (IndexError, AttributeError):
                    continue

        if not gastos_mensuales:
            raise ValueError("No hay gastos registrados para generar la comparativa.")

        # Ordenamos cronológicamente
        try:
            return dict(
                sorted(gastos_mensuales.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y"))
            )
        except ValueError:
            return dict(sorted(gastos_mensuales.items()))

    def _variacion_porcentual(self, anterior, actual):
        """Calcula la variación porcentual entre dos valores."""
        if anterior == 0:
            return None  # Evita división entre cero
        return ((actual - anterior) / anterior) * 100

    def mostrar_comparativa(self):
        """Imprime la comparativa de gastos mes a mes con variación porcentual."""
        try:
            datos = self.obtener_gastos_por_mes()
        except ValueError as e:
            print(f"\n{e}")
            return

        meses = list(datos.keys())
        print(f"\n{'─'*50}")
        print(f"  COMPARATIVA DE GASTOS MENSUALES")
        print(f"{'─'*50}")

        for i, mes in enumerate(meses):
            if i == 0:
                print(f"  {mes}:  {datos[mes]:>9.2f}€")
            else:
                anterior = datos[meses[i - 1]]
                actual = datos[mes]
                variacion = self._variacion_porcentual(anterior, actual)
                if variacion is None:
                    flecha = "  →"
                    variacion_str = "n/d"
                elif variacion > 0:
                    flecha = "  ▲"
                    variacion_str = f"+{variacion:.1f}%"
                elif variacion < 0:
                    flecha = "  ▼"
                    variacion_str = f"{variacion:.1f}%"
                else:
                    flecha = "  ─"
                    variacion_str = "0.0%"

                print(f"  {mes}:  {actual:>9.2f}€  {flecha} {variacion_str}")

        print(f"{'─'*50}")

        # Resumen final si hay al menos 2 meses
        if len(meses) >= 2:
            ultimo = meses[-1]
            penultimo = meses[-2]
            dif = datos[ultimo] - datos[penultimo]
            variacion = self._variacion_porcentual(datos[penultimo], datos[ultimo])

            tendencia = "incrementado" if dif > 0 else ("reducido" if dif < 0 else "mantenido igual")
            print(f"\n  Respecto a {penultimo}, tus gastos se han {tendencia} en {abs(dif):.2f}€", end="")
            if variacion is not None:
                print(f" ({abs(variacion):.1f}%)", end="")
            print()

        # Mes con mayor y menor gasto
        mes_max = max(datos, key=datos.get)
        mes_min = min(datos, key=datos.get)
        print(f"\n  Mes con más gasto:  {mes_max} ({datos[mes_max]:.2f}€)")
        print(f"  Mes con menos gasto: {mes_min} ({datos[mes_min]:.2f}€)")
        print(f"{'─'*50}")
