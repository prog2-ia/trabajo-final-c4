from Ingreso import Ingreso
from Excepciones import (
    TransaccionNoEncontradaError,
    CuentaNoInicializadaError,
    SaldoInsuficienteError,
)


class Cuenta:
    def __init__(self, nombre, saldo_inicial=0.0, restringir_saldo_negativo=False):
        """
        :param nombre: Nombre del titular de la cuenta.
        :param saldo_inicial: Saldo de partida (puede ser 0).
        :param restringir_saldo_negativo: Si True, impide gastos que dejen el saldo en negativo.
        """
        if not nombre or not str(nombre).strip():
            raise CuentaNoInicializadaError()
        self.nombre = str(nombre).strip()
        self.saldo = saldo_inicial
        self.transacciones = []
        self.restringir_saldo_negativo = restringir_saldo_negativo

    # ── Magia de Python: Métodos Especiales (T07 y T08) ──────────────────────

    def __str__(self):
        """
        Reemplaza al antiguo método mostrar().
        Devuelve una representación en texto para que funcione directamente con print(cuenta).
        """
        lineas = [f"\nCuenta: {self.nombre}"]
        if not self.transacciones:
            lineas.append("  (Sin movimientos registrados)")
        else:
            for t in self.transacciones:
                # NOTA: Usamos t.mostrar() asumiendo que aún no habéis
                # implementado __str__ en la clase Transaccion.
                lineas.append(f"  {t.mostrar()}")
        lineas.append(f"Saldo actual: {self.saldo:.2f}€")
        return "\n".join(lineas)

    def __len__(self):
        """
        Sobrecarga de len(). Permite usar len(cuenta) para obtener
        el número total de transacciones de forma nativa.
        """
        return len(self.transacciones)

    def __iadd__(self, transaccion):
        """
        Sobrecarga del operador +=.
        Permite hacer de forma elegante: cuenta += nueva_transaccion
        """
        self.agregar_transaccion(transaccion)
        return self


    # ── Gestión de transacciones ─────────────────────────────────────────────

    def agregar_transaccion(self, transaccion):
        """Añade una transacción y actualiza el saldo."""
        if isinstance(transaccion, Ingreso):
            self.saldo += transaccion.importe
        else:
            if self.restringir_saldo_negativo and transaccion.importe > self.saldo:
                raise SaldoInsuficienteError(self.saldo, transaccion.importe)
            self.saldo -= transaccion.importe

        self.transacciones.append(transaccion)

    def eliminar_transaccion(self, concepto):
        """
        Elimina la primera transacción que coincida con el concepto dado
        y revierte su efecto en el saldo.

        :raises TransaccionNoEncontradaError: Si no existe ninguna con ese concepto.
        """
        concepto = concepto.strip().lower()
        for t in self.transacciones:
            if t.concepto.lower() == concepto:
                # Revertir el efecto en el saldo
                if isinstance(t, Ingreso):
                    self.saldo -= t.importe
                else:
                    self.saldo += t.importe
                self.transacciones.remove(t)
                print(f"Transacción '{t.concepto}' eliminada correctamente.")
                return
        raise TransaccionNoEncontradaError(concepto)

    def buscar_por_concepto(self, termino):
        """
        Devuelve una lista de transacciones cuyo concepto contenga el término buscado
        (búsqueda insensible a mayúsculas).

        :raises TransaccionNoEncontradaError: Si no se encuentra ninguna.
        """
        termino = termino.strip().lower()
        resultados = [t for t in self.transacciones if termino in t.concepto.lower()]
        if not resultados:
            raise TransaccionNoEncontradaError(termino)
        return resultados

    def buscar_por_categoria(self, categoria):
        """Devuelve todas las transacciones de una categoría concreta."""
        categoria = categoria.strip().lower()
        resultados = [t for t in self.transacciones if t.categoria.lower() == categoria]
        if not resultados:
            raise TransaccionNoEncontradaError(f"categoría '{categoria}'")
        return resultados

    def buscar_por_rango_fechas(self, fecha_inicio, fecha_fin):
        """
        Devuelve transacciones entre dos fechas (formato DD/MM/YYYY, ambas inclusive).

        :raises ValueError: Si las fechas tienen formato incorrecto.
        """
        from datetime import datetime
        fmt = "%d/%m/%Y"
        try:
            dt_inicio = datetime.strptime(fecha_inicio, fmt)
            dt_fin = datetime.strptime(fecha_fin, fmt)
        except ValueError:
            raise ValueError(f"Formato de fecha incorrecto. Usa DD/MM/YYYY.")

        if dt_inicio > dt_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

        resultados = [
            t for t in self.transacciones
            if dt_inicio <= t.fecha_como_datetime() <= dt_fin
        ]
        if not resultados:
            raise TransaccionNoEncontradaError(f"rango {fecha_inicio} - {fecha_fin}")
        return resultados

    # ── Estadísticas ─────────────────────────────────────────────────────────

    def obtener_gastos_por_categoria(self):
        """Agrupa todos los gastos por categoría y calcula el total de cada una."""
        categorias = {}
        for t in self.transacciones:
            if not isinstance(t, Ingreso):
                categorias[t.categoria] = categorias.get(t.categoria, 0) + t.importe
        return categorias

    def obtener_ingresos_por_categoria(self):
        """Agrupa todos los ingresos por categoría."""
        categorias = {}
        for t in self.transacciones:
            if isinstance(t, Ingreso):
                categorias[t.categoria] = categorias.get(t.categoria, 0) + t.importe
        return categorias

    def balance_ingresos_gastos(self):
        """Devuelve (total_ingresos, total_gastos, diferencia)."""
        total_ingresos = sum(t.importe for t in self.transacciones if isinstance(t, Ingreso))
        total_gastos = sum(t.importe for t in self.transacciones if not isinstance(t, Ingreso))
        return total_ingresos, total_gastos, total_ingresos - total_gastos

    # ── Informes ─────────────────────────────────────────────────────────────

    def mostrar_reporte_categorias(self):
        """Muestra el gasto por categorías con porcentaje sobre el total."""
        datos = self.obtener_gastos_por_categoria()
        if not datos:
            print("No hay gastos registrados para generar estadísticas.")
            return

        total_gastos = sum(datos.values())
        print(f"\n--- ANÁLISIS DE GASTOS POR CATEGORÍA ---")
        for cat, monto in sorted(datos.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (monto / total_gastos) * 100
            barra = "█" * int(porcentaje / 5)  # barra visual proporcional
            print(f"• {cat:<20} {monto:>8.2f}€  ({porcentaje:5.1f}%)  {barra}")
        print(f"{'─'*40}")
        print(f"  TOTAL GASTADO: {total_gastos:.2f}€")

    def generar_resumen(self):
        """Imprime un resumen completo de la cuenta."""
        total_ingresos, total_gastos, diferencia = self.balance_ingresos_gastos()

        print(f"\n{'='*45}")
        print(f"   RESUMEN DE CUENTA: {self.nombre}")
        print(f"{'='*45}")
        print(f"  Saldo actual:        {self.saldo:>10.2f}€")
        print(f"  Total ingresos:      {total_ingresos:>10.2f}€")
        print(f"  Total gastos:        {total_gastos:>10.2f}€")
        print(f"  Diferencia neta:     {diferencia:>10.2f}€")
        print(f"  Nº de transacciones: {len(self):>10}") # <--- ¡Aquí estamos usando __len__!
        print(f"{'─'*45}")

        print("\n--- ÚLTIMOS 10 MOVIMIENTOS ---")
        for t in reversed(self.transacciones[-10:]):
            print(f"  {t.mostrar()}")
        print(f"{'='*45}")