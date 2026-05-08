from Ingreso import Ingreso


class Cuenta:
    def __init__(self, nombre):
        self.nombre = nombre
        self.transacciones = []
        self.saldo = 0

    def agregar_transaccion(self, transaccion):
        self.transacciones.append(transaccion)

        # CORRECCIÓN: Usamos isinstance para incluir Ingreso e IngresoFijo
        if isinstance(transaccion, Ingreso):
            self.saldo += transaccion.importe
        else:
            self.saldo -= transaccion.importe

    def generar_resumen(self):
        print(f"\n===== RESUMEN DE CUENTA: {self.nombre} =====")
        print(f"Saldo Actual: {self.saldo}€")

        # Separamos ingresos y gastos para el análisis
        gastos = [t for t in self.transacciones if not isinstance(t, Ingreso)]
        total_gastos = sum(g.importe for g in gastos)

        print(f"Transacciones totales: {len(self.transacciones)}")
        print(f"Gasto total acumulado: {total_gastos}€")

        print("\n--- ÚLTIMOS 10 MOVIMIENTOS ---")
        # Mostramos los 10 más recientes (del último al primero)
        for t in reversed(self.transacciones[-10:]):
            print(t.mostrar())
        print("===========================================")

    def mostrar(self):
        print(f"\nCuenta: {self.nombre}")
        print("Movimientos:")
        for t in self.transacciones:
            print(t.mostrar())
        print(f"Saldo actual: {self.saldo}€")

    def obtener_gastos_por_categoria(self):
        """Agrupa todos los gastos por su categoría y calcula el total de cada una."""
        # Diccionario para { "Categoría": total_acumulado }
        categorias = {}

        for t in self.transacciones:
            # Solo sumamos si es una instancia de Gasto (o sus derivados como GastoFijo)
            # Usamos 'not isinstance(t, Ingreso)' para capturar cualquier tipo de gasto
            if not isinstance(t, Ingreso):
                cat = t.categoria
                if cat in categorias:
                    categorias[cat] += t.importe
                else:
                    categorias[cat] = t.importe

        return categorias

    def mostrar_reporte_categorias(self):
        """Muestra de forma visual el gasto por categorías y el porcentaje sobre el total."""
        datos = self.obtener_gastos_por_categoria()

        if not datos:
            print("No hay gastos registrados para generar estadísticas.")
            return

        total_gastos = sum(datos.values())

        print(f"\n--- ANÁLISIS DE GASTOS POR CATEGORÍA ---")
        # Ordenamos de mayor a menor gasto
        for cat, monto in sorted(datos.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (monto / total_gastos) * 100
            print(f"• {cat}: {monto:.2f}€ ({porcentaje:.1f}%)")
        print(f"----------------------------------------")
        print(f"TOTAL GASTADO: {total_gastos:.2f}€")