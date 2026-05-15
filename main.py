from datetime import datetime
from DetectarAnomalia import DetectorAnomalias
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso
from GastoFijo import GastoFijo
from IngresoFijo import IngresoFijo
from Presupuesto import Presupuesto
from Comparar import Comparador
from GestorArchivos import GestorArchivos
from Excepciones import (
    FinanzasError,
    ImporteInvalidoError,
    FechaInvalidaError,
    ConceptoVacioError,
    PresupuestoInvalidoError,
    PresupuestoDuplicadoError,
    TransaccionNoEncontradaError,
    SaldoInsuficienteError,
    ArchivoCorruptoError,
)


def mostrar_menu():
    print("\n" + "=" * 35)
    print("   GESTOR DE FINANZAS v4.0")
    print("=" * 35)
    print(" 1. Añadir ingreso (Puntual o Fijo)")
    print(" 2. Añadir gasto   (Puntual o Fijo)")
    print(" 3. Mostrar todas las transacciones")
    print(" 4. Mostrar saldo actual")
    print(" 5. Crear presupuesto mensual")
    print(" 6. Comparar dos presupuestos")
    print(" 7. Salir y Guardar")
    print(" 8. Comparar gastos mensuales (histórico)")
    print(" 9. Generar resumen detallado")
    print("10. Buscar transacción por concepto")
    print("11. Eliminar transacción por concepto")
    print("12. Ver estado de un presupuesto")
    print("13. Informe de anomalías completo")
    print("14. Exportar informe a TXT")
    print("15. Buscar transacciones por rango de fechas")
    print("=" * 35)


def pedir_importe(mensaje="Importe: "):
    """Solicita un importe válido al usuario con manejo de excepciones."""
    while True:
        try:
            valor = float(input(mensaje))
            if valor <= 0:
                raise ImporteInvalidoError(valor)
            return valor
        except ImporteInvalidoError as e:
            print(f"  Error: {e}")
        except ValueError:
            print("  Error: Introduce un número válido.")


def pedir_fecha(mensaje="Fecha (DD/MM/YYYY) o ENTER para hoy: "):
    """Solicita una fecha válida al usuario."""
    while True:
        entrada = input(mensaje).strip()
        if entrada == "":
            return datetime.today().strftime("%d/%m/%Y")
        try:
            datetime.strptime(entrada, "%d/%m/%Y")
            return entrada
        except ValueError:
            raise FechaInvalidaError(entrada)


def pedir_transaccion(tipo):
    """Solicita los datos de una transacción al usuario."""
    while True:
        concepto = input("Concepto: ").strip()
        if concepto:
            break
        print("  Error: El concepto no puede estar vacío.")

    importe = pedir_importe()

    while True:
        categoria = input("Categoría: ").strip()
        if categoria:
            break
        print("  Error: La categoría no puede estar vacía.")

    while True:
        try:
            fecha = pedir_fecha()
            break
        except FechaInvalidaError as e:
            print(f"  Error: {e}")

    if tipo == "ingreso":
        origen = input("Origen del ingreso (ej. Empresa, Regalo): ").strip() or "Desconocido"
        es_fijo = input("¿Es un ingreso fijo/recurrente? (s/n): ").lower()
        if es_fijo == 's':
            frecuencia = input("Frecuencia (Mensual/Semanal/Anual): ").strip() or "Mensual"
            return IngresoFijo(concepto, importe, categoria, fecha, origen, frecuencia)
        return Ingreso(concepto, importe, categoria, fecha, origen)
    else:
        metodo_pago = input("Método de pago (ej. Tarjeta, Efectivo): ").strip() or "Efectivo"
        es_fijo = input("¿Es un gasto fijo/recurrente? (s/n): ").lower()
        if es_fijo == 's':
            frecuencia = input("Frecuencia (Mensual/Anual): ").strip() or "Mensual"
            return GastoFijo(concepto, importe, categoria, fecha, metodo_pago, frecuencia)
        return Gasto(concepto, importe, categoria, fecha, metodo_pago)


def main():
    # ── Carga inicial ────────────────────────────────────────────────────────
    cuenta = None
    try:
        cuenta = GestorArchivos.cargar_datos()
    except ArchivoCorruptoError as e:
        print(f"\n⚠  Advertencia: {e}")
        print("Se iniciará una cuenta nueva.")

    if cuenta is None:
        print("No se encontraron datos previos.")
        nombre = input("Nombre del titular de la cuenta: ").strip()
        if not nombre:
            nombre = "Mi Cuenta"
        cuenta = Cuenta(nombre)
        cuenta.saldo = pedir_importe("Saldo inicial: ")
    else:
        print(f"\n✔  Sesión cargada: Cuenta de {cuenta.nombre}")

    detector = DetectorAnomalias()
    presupuestos = {}  # { "MesCapitalizado": Presupuesto }

    # ── Bucle principal ──────────────────────────────────────────────────────
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()

        # ── 1: Añadir ingreso ────────────────────────────────────────────────
        if opcion == "1":
            try:
                ingreso = pedir_transaccion("ingreso")
                cuenta.agregar_transaccion(ingreso)
                print(f"  ✔  Ingreso '{ingreso.concepto}' registrado.")
            except FinanzasError as e:
                print(f"  ✘  Error: {e}")

        # ── 2: Añadir gasto ──────────────────────────────────────────────────
        elif opcion == "2":
            try:
                gasto = pedir_transaccion("gasto")

                umbral = detector.calcular_umbral_dinamico(cuenta.transacciones)
                if umbral > 0 and gasto.importe > umbral:
                    print(f"\n  ⚠  ALERTA: Este gasto ({gasto.importe:.2f}€) supera el umbral ({umbral:.2f}€).")
                    if input("  ¿Confirmar de todas formas? (s/n): ").lower() != 's':
                        print("  Operación cancelada.")
                        continue

                cuenta.agregar_transaccion(gasto)
                print(f"  ✔  Gasto '{gasto.concepto}' registrado.")

            except SaldoInsuficienteError as e:
                print(f"  ✘  {e}")
            except FinanzasError as e:
                print(f"  ✘  Error: {e}")

        # ── 3: Mostrar transacciones ─────────────────────────────────────────
        elif opcion == "3":
            cuenta.mostrar()
            cuenta.mostrar_reporte_categorias()

        # ── 4: Saldo ─────────────────────────────────────────────────────────
        elif opcion == "4":
            total_ing, total_gas, dif = cuenta.balance_ingresos_gastos()
            print(f"\n  Saldo actual:    {cuenta.saldo:.2f}€")
            print(f"  Total ingresos:  {total_ing:.2f}€")
            print(f"  Total gastos:    {total_gas:.2f}€")
            print(f"  Balance neto:    {dif:.2f}€")

        # ── 5: Crear presupuesto ─────────────────────────────────────────────
        elif opcion == "5":
            try:
                mes = input("Mes (ej. Mayo): ").strip().capitalize()
                if not mes:
                    raise ValueError("El mes no puede estar vacío.")
                if mes in presupuestos:
                    raise PresupuestoDuplicadoError(mes)
                monto = pedir_importe("Cantidad presupuestada: ")
                presupuestos[mes] = Presupuesto(mes, monto)
                print(f"  ✔  Presupuesto para {mes} creado: {monto:.2f}€")
            except PresupuestoDuplicadoError as e:
                print(f"  ✘  {e}")
            except PresupuestoInvalidoError as e:
                print(f"  ✘  {e}")
            except ValueError as e:
                print(f"  ✘  Error: {e}")

        # ── 6: Comparar presupuestos ─────────────────────────────────────────
        elif opcion == "6":
            if len(presupuestos) < 2:
                print("  Se necesitan al menos 2 presupuestos.")
            else:
                lista = list(presupuestos.values())
                for i, p in enumerate(lista, 1):
                    print(f"  {i}. {p.mes}: {p.cantidad:.2f}€")
                try:
                    idx1 = int(input("Primer presupuesto (número): ")) - 1
                    idx2 = int(input("Segundo presupuesto (número): ")) - 1
                    if not (0 <= idx1 < len(lista)) or not (0 <= idx2 < len(lista)):
                        raise IndexError
                    res = lista[idx1].comparar(lista[idx2])
                    mayor = lista[idx1].mes if res else lista[idx2].mes
                    print(f"  El presupuesto mayor es el de {mayor}.")
                except (ValueError, IndexError):
                    print("  ✘  Selección inválida.")

        # ── 7: Guardar y salir ───────────────────────────────────────────────
        elif opcion == "7":
            try:
                GestorArchivos.guardar_datos(cuenta)
                print("  ¡Hasta pronto!")
            except IOError as e:
                print(f"  ✘  {e}")
            break

        # ── 8: Comparativa mensual ───────────────────────────────────────────
        elif opcion == "8":
            Comparador(cuenta).mostrar_comparativa()

        # ── 9: Resumen detallado ─────────────────────────────────────────────
        elif opcion == "9":
            cuenta.generar_resumen()

        # ── 10: Buscar transacción ───────────────────────────────────────────
        elif opcion == "10":
            termino = input("Concepto a buscar: ").strip()
            try:
                resultados = cuenta.buscar_por_concepto(termino)
                print(f"\n  Se encontraron {len(resultados)} resultado(s):")
                for t in resultados:
                    print(f"  → {t.mostrar()}")
            except TransaccionNoEncontradaError as e:
                print(f"  ✘  {e}")

        # ── 11: Eliminar transacción ─────────────────────────────────────────
        elif opcion == "11":
            concepto = input("Concepto exacto a eliminar: ").strip()
            try:
                cuenta.eliminar_transaccion(concepto)
            except TransaccionNoEncontradaError as e:
                print(f"  ✘  {e}")

        # ── 12: Estado de presupuesto ────────────────────────────────────────
        elif opcion == "12":
            if not presupuestos:
                print("  No hay presupuestos creados.")
            else:
                for i, mes in enumerate(presupuestos, 1):
                    print(f"  {i}. {mes}")
                try:
                    idx = int(input("Selecciona el presupuesto: ")) - 1
                    mes_sel = list(presupuestos.keys())[idx]
                    presupuestos[mes_sel].mostrar_estado(cuenta)
                except (ValueError, IndexError):
                    print("  ✘  Selección inválida.")

        # ── 13: Informe de anomalías ─────────────────────────────────────────
        elif opcion == "13":
            detector.informe_anomalias(cuenta.transacciones)

        # ── 14: Exportar a TXT ───────────────────────────────────────────────
        elif opcion == "14":
            nombre_archivo = input("Nombre del archivo (ENTER = 'informe.txt'): ").strip()
            if not nombre_archivo:
                nombre_archivo = "informe.txt"
            if not nombre_archivo.endswith(".txt"):
                nombre_archivo += ".txt"
            try:
                GestorArchivos.exportar_informe_txt(cuenta, nombre_archivo)
            except IOError as e:
                print(f"  ✘  {e}")

        # ── 15: Buscar por rango de fechas ───────────────────────────────────
        elif opcion == "15":
            try:
                fecha_ini = pedir_fecha("Fecha inicio (DD/MM/YYYY): ")
                fecha_fin = pedir_fecha("Fecha fin   (DD/MM/YYYY): ")
                resultados = cuenta.buscar_por_rango_fechas(fecha_ini, fecha_fin)
                print(f"\n  {len(resultados)} transacción(es) entre {fecha_ini} y {fecha_fin}:")
                for t in resultados:
                    print(f"  → {t.mostrar()}")
            except (TransaccionNoEncontradaError, ValueError) as e:
                print(f"  ✘  {e}")
            except FechaInvalidaError as e:
                print(f"  ✘  {e}")

        else:
            print("  Opción no válida. Elige entre 1 y 15.")


if __name__ == "__main__":
    main()
