from Gasto import Gasto
from datetime import datetime


class Comparador:
    def __init__(self, cuenta):
        self.cuenta = cuenta

    def obtener_gastos_por_mes(self):
        # Diccionario para guardar { "MM/YYYY": suma_gastos }
        gastos_mensuales = {}

        for t in self.cuenta.transacciones:
            if isinstance(t, Gasto):
                try:
                    partes_fecha = t.fecha.split('/')
                    if len(partes_fecha) == 3:
                        # Usamos MM/YYYY como clave
                        mes_año = f"{partes_fecha[1]}/{partes_fecha[2]}"

                        if mes_año in gastos_mensuales:
                            gastos_mensuales[mes_año] += t.importe
                        else:
                            gastos_mensuales[mes_año] = t.importe
                except (IndexError, AttributeError):
                    # Si la fecha no tiene el formato esperado, saltamos esa transacción
                    continue

        return gastos_mensuales

    def mostrar_comparativa(self):
        datos = self.obtener_gastos_por_mes()
        if not datos:
            print("No hay suficientes datos de gastos para comparar.")
            return

        print("\nCOMPARATIVA DE GASTOS MENSUALES")

        # Ordenamos los meses cronológicamente para que la comparativa tenga sentido
        try:
            meses_ordenados = sorted(datos.keys(), key=lambda x: datetime.strptime(x, "%m/%Y"))
        except ValueError:
            # Si el ordenamiento falla, usamos el orden por defecto
            meses_ordenados = sorted(datos.keys())

        for mes in meses_ordenados:
            print(f"Mes {mes}: {datos[mes]:.2f}€")

        if len(meses_ordenados) >= 2:
            ultimo = meses_ordenados[-1]
            penultimo = meses_ordenados[-2]
            dif = datos[ultimo] - datos[penultimo]
            sube_baja = "incrementado" if dif > 0 else "reducido"
            print(f"\nRespecto al mes anterior ({penultimo}), tus gastos se han {sube_baja} en {abs(dif):.2f}€.")