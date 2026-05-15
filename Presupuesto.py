from Excepciones import PresupuestoInvalidoError


class Presupuesto:
    MESES_VALIDOS = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    def __init__(self, mes, cantidad):
        """
        :param mes: Nombre del mes (ej. "Mayo").
        :param cantidad: Cantidad presupuestada (> 0).
        :raises PresupuestoInvalidoError: Si la cantidad no es válida.
        """
        try:
            cantidad = float(cantidad)
        except (TypeError, ValueError):
            raise PresupuestoInvalidoError(cantidad)
        if cantidad <= 0:
            raise PresupuestoInvalidoError(cantidad)

        self.mes = str(mes).strip().capitalize()
        self.cantidad = cantidad

    # ── Operaciones ──────────────────────────────────────────────────────────

    def sumar(self, otro):
        """Devuelve la suma de dos presupuestos."""
        if not isinstance(otro, Presupuesto):
            raise TypeError("Solo se pueden sumar dos objetos Presupuesto.")
        return self.cantidad + otro.cantidad

    def comparar(self, otro):
        """Devuelve True si este presupuesto es mayor que 'otro'."""
        if not isinstance(otro, Presupuesto):
            raise TypeError("Solo se pueden comparar dos objetos Presupuesto.")
        return self.cantidad > otro.cantidad

    def estado_presupuesto(self, cuenta):
        """
        Compara el presupuesto con los gastos reales del mes en la cuenta dada.
        Devuelve un dict con: gastado, presupuestado, restante, porcentaje_usado, en_superavit.

        :param cuenta: Objeto Cuenta del que extraer los gastos.
        """
        from Ingreso import Ingreso

        mes_lower = self.mes.lower()
        mes_index = None

        for i, m in enumerate(self.MESES_VALIDOS, start=1):
            if m == mes_lower:
                mes_index = i
                break

        if mes_index is None:
            # Si el mes no coincide con ninguno conocido, calculamos sobre todos los gastos
            gastos_del_mes = [t for t in cuenta.transacciones if not isinstance(t, Ingreso)]
        else:
            gastos_del_mes = [
                t for t in cuenta.transacciones
                if not isinstance(t, Ingreso)
                and int(t.fecha.split('/')[1]) == mes_index
            ]

        gastado = sum(t.importe for t in gastos_del_mes)
        restante = self.cantidad - gastado
        porcentaje = (gastado / self.cantidad) * 100 if self.cantidad > 0 else 0

        return {
            "gastado": gastado,
            "presupuestado": self.cantidad,
            "restante": restante,
            "porcentaje_usado": porcentaje,
            "en_superavit": restante >= 0,
        }

    def mostrar_estado(self, cuenta):
        """Imprime un resumen visual del estado del presupuesto."""
        estado = self.estado_presupuesto(cuenta)
        simbolo = "✔" if estado["en_superavit"] else "✘"

        print(f"\n--- PRESUPUESTO: {self.mes} ---")
        print(f"  Presupuestado: {estado['presupuestado']:.2f}€")
        print(f"  Gastado:       {estado['gastado']:.2f}€  ({estado['porcentaje_usado']:.1f}%)")
        print(f"  Restante:      {estado['restante']:.2f}€  {simbolo}")
        if not estado["en_superavit"]:
            exceso = abs(estado["restante"])
            print(f"  ¡Atención! Has superado el presupuesto en {exceso:.2f}€")

    def mostrar(self):
        print(f"{self.mes}: {self.cantidad:.2f}€")

    def __repr__(self):
        return f"Presupuesto(mes='{self.mes}', cantidad={self.cantidad})"
