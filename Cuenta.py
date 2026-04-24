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