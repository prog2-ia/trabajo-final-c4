from datetime import datetime
from DetectarAnomalia import DetectorAnomalias
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso
from GastoFijo import GastoFijo
from IngresoFijo import IngresoFijo  # <--- Importante añadir esta clase
from Presupuesto import Presupuesto
from Comparar import Comparador
from GestorArchivos import GestorArchivos


def mostrar_menu():
    print("\n" + "=" * 30)
    print("   GESTOR DE FINANZAS v3.0")
    print("=" * 30)
    print("1. Añadir ingreso (Puntual o Fijo)")
    print("2. Añadir gasto (Puntual o Fijo)")
    print("3. Mostrar todas las transacciones")
    print("4. Mostrar saldo actual")
    print("5. Crear presupuesto mensual")
    print("6. Comparar presupuestos")
    print("7. Salir y Guardar")
    print("8. Comparar gastos mensuales (Histórico)")
    print("9. Generar resumen detallado (Top 10)")
    print("=" * 30)


def pedir_transaccion(tipo):
    concepto = input("Concepto: ")
    while True:
        try:
            importe = float(input("Importe: "))
            if importe <= 0:
                raise ValueError
            break
        except ValueError:
            print("Error: Introduce un número válido y mayor a 0.")

    categoria = input("Categoría: ")
    fecha = input("Fecha (DD/MM/YYYY) o ENTER para hoy: ")
    if fecha.strip() == "":
        fecha = datetime.today().strftime("%d/%m/%Y")

    if tipo == "ingreso":
        origen = input("Origen del ingreso (ej. Empresa, Regalo): ")
        es_fijo = input("¿Es un ingreso fijo/recurrente? (s/n): ").lower()
        if es_fijo == 's':
            frecuencia = input("Frecuencia (Mensual/Semanal): ")
            return IngresoFijo(concepto, importe, categoria, fecha, origen, frecuencia)
        return Ingreso(concepto, importe, categoria, fecha, origen)
    else:
        metodo_pago = input("Método de pago (ej. Tarjeta, Efectivo): ")
        es_fijo = input("¿Es un gasto fijo/recurrente? (s/n): ").lower()
        if es_fijo == 's':
            frecuencia = input("Frecuencia (Mensual/Anual): ")
            return GastoFijo(concepto, importe, categoria, fecha, metodo_pago, frecuencia)
        return Gasto(concepto, importe, categoria, fecha, metodo_pago)


def main():
    # Carga automática al iniciar desde el CSV
    cuenta = GestorArchivos.cargar_datos()

    if cuenta is None:
        print("No se han encontrado datos previos.")
        nombre_cuenta = input("Nombre del titular de la cuenta: ")
        cuenta = Cuenta(nombre_cuenta)
        try:
            saldo_ini = float(input("Saldo inicial de la cuenta: "))
            cuenta.saldo = saldo_ini
        except ValueError:
            cuenta.saldo = 0
    else:
        print(f"\n--- Sesión cargada: Cuenta de {cuenta.nombre} ---")

    detector = DetectorAnomalias()
    presupuestos = []

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            ingreso = pedir_transaccion("ingreso")
            cuenta.agregar_transaccion(ingreso)
            print("✓ Ingreso registrado correctamente.")

        elif opcion == "2":
            gasto = pedir_transaccion("gasto")

            # Verificación de anomalías (solo para gastos)
            umbral = detector.calcular_umbral_dinamico(cuenta.transacciones)
            if umbral > 0 and gasto.importe > umbral:
                print(f"\n⚠️ ALERTA DE GASTO ELEVADO")
                print(f"Este gasto ({gasto.importe}€) supera tu umbral de seguridad ({umbral:.2f}€).")
                if input("¿Confirmar registro de todas formas? (s/n): ").lower() != 's':
                    print("Operación cancelada.")
                    continue

            cuenta.agregar_transaccion(gasto)
            print("✓ Gasto registrado correctamente.")

        elif opcion == "3":
            cuenta.mostrar()

        elif opcion == "4":
            print(f"\n💰 Saldo disponible actual: {cuenta.saldo}€")

        elif opcion == "5":
            mes = input("Mes (ej. Mayo): ")
            try:
                monto = float(input("Cantidad presupuestada: "))
                presupuestos.append(Presupuesto(mes, monto))
                print(f"✓ Presupuesto para {mes} creado.")
            except ValueError:
                print("Error: La cantidad debe ser un número.")

        elif opcion == "6":
            if len(presupuestos) < 2:
                print("Se necesitan al menos 2 presupuestos para realizar la comparativa.")
            else:
                for i, p in enumerate(presupuestos):
                    print(f"{i + 1}. {p.mes}: {p.cantidad}€")
                try:
                    idx1 = int(input("Primer presupuesto (número): ")) - 1
                    idx2 = int(input("Segundo presupuesto (número): ")) - 1
                    res = presupuestos[idx1].comparar(presupuestos[idx2])
                    print(f"¿Es {presupuestos[idx1].mes} mayor que {presupuestos[idx2].mes}?: {'SÍ' if res else 'NO'}")
                except:
                    print("Error: Selección de presupuestos inválida.")

        elif opcion == "8":
            comp = Comparador(cuenta)
            comp.mostrar_comparativa()

        elif opcion == "9":
            # Si has implementado el método en Cuenta.py se llama aquí
            if hasattr(cuenta, 'generar_resumen'):
                cuenta.generar_resumen()
            else:
                # Versión rápida por si no has actualizado Cuenta.py todavía
                print(f"\n{'=' * 20} RESUMEN {'=' * 20}")
                print(f"Saldo Total: {cuenta.saldo}€")
                print(f"Últimos 10 movimientos registrados:")
                for t in cuenta.transacciones[-10:]:
                    print(t.mostrar())
                print('=' * 49)

        elif opcion == "7":
            GestorArchivos.guardar_datos(cuenta)
            print("Guardando cambios en datos.csv... ¡Hasta pronto!")
            break

        else:
            print("Opción no válida. Por favor, elige una del 1 al 9.")


if __name__ == "__main__":
    main()