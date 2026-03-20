from Gasto import Gasto


class Comparador:
    def __init__(self, cuenta):
        self.cuenta = cuenta

    def obtener_gastos_por_mes(self):
        # Diccionario para guardar { "MM/YYYY": suma_gastos }
        gastos_mensuales = {}

        for t in self.cuenta.transacciones:
            if isinstance(t, Gasto):
                # Extraemos el mes y año de la fecha (asumiendo formato DD/MM/YYYY)
                partes_fecha = t.fecha.split('/')
                if len(partes_fecha) == 3:
                    mes_año = f"{partes_fecha[1]}/{partes_fecha[2]}"

                    if mes_año in gastos_mensuales:
                        gastos_mensuales[mes_año] += t.importe
                    else:
                        gastos_mensuales[mes_año] = t.importe

        return gastos_mensuales

    def mostrar_comparativa(self):
        datos = self.obtener_gastos_por_mes()
        if not datos:
            print("No hay suficientes datos de gastos para comparar.")
            return

        print("\n--- COMPARATIVA DE GASTOS MENSUALES ---")
        # Ordenamos los meses (esto es un poco básico, pero funciona)
        for mes, total in sorted(datos.items()):
            print(f"Mes {mes}: {total}€")

        # Lógica de comparación simple
        meses = list(datos.keys())
        if len(meses) >= 2:
            ultimo = meses[-1]
            penultimo = meses[-2]
            dif = datos[ultimo] - datos[penultimo]
            sube_baja = "incrementado" if dif > 0 else "reducido"
            print(f"\n Respecto al mes anterior, tus gastos se han {sube_baja} en {abs(dif)}€.")