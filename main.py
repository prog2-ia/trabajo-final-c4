from datetime import datetime
from DetectarAnomalia import DetectorAnomalias
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso
from Presupuesto import Presupuesto
from Comparar import Comparador
from Transaccion import Transaccion
from GestorArchivos import GestorArchivos  # <--- Importamos nuestro nuevo gestor CSV



def mostrar_menu():
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Añadir ingreso")
    print("2. Añadir gasto")
    print("3. Mostrar transacciones")
    print("4. Mostrar saldo")
    print("5. Crear presupuesto")
    print("6. Comparar presupuestos")
    print("7. Salir y Guardar")  # <--- Actualizado
    print("8. Comparar gastos mensuales")  # <--- AÑADIDO AL MENÚ


def pedir_transaccion(tipo):
    concepto = input("Concepto: ")
    while True:
        try:
            importe = float(input("Importe: "))
            if importe <= 0:
                raise ValueError
            break
        except ValueError:
            print("Introduce un importe válido (>0)")
    categoria = input("Categoría: ")
    fecha = input("Fecha (DD/MM/YYYY) o ENTER para hoy: ")
    if fecha.strip() == "":
        fecha = datetime.today().strftime("%d/%m/%Y")

    if tipo == "ingreso":
        origen = input("Origen: ")
        return Ingreso(concepto, importe, categoria, fecha, origen)
    else:
        metodo_pago = input("Método de pago: ")
        return Gasto(concepto, importe, categoria, fecha, metodo_pago)



if __name__ == "__main__":

    # Intentamos cargar los datos del CSV al iniciar
    print("Buscando datos guardados en CSV...")
    cuenta = GestorArchivos.cargar_datos()

    # Si no hay CSV, pedimos los datos
    if cuenta is None:
        print("No se encontraron datos previos. Creando una nueva cuenta.")
        nombre_cuenta = input("Introduce el nombre de tu cuenta: ")
        while True:
            try:
                saldo_inicial = float(input("Saldo inicial: "))
                if saldo_inicial < 0:
                    raise ValueError
                break
            except ValueError:
                print("Introduce un saldo válido (>=0)")

        cuenta = Cuenta(nombre_cuenta)
        cuenta.saldo = saldo_inicial
    else:
        print(f"Datos cargados con éxito. ¡Hola de nuevo! Cuenta: {cuenta.nombre}")

    presupuestos = []
    detector = DetectorAnomalias()

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ")

        if opcion == "1":
            ingreso = pedir_transaccion("ingreso")
            cuenta.agregar_transaccion(ingreso)
            print("Ingreso añadido correctamente")

        elif opcion == "2":
            gasto = pedir_transaccion("gasto")
            umbral = detector.calcular_umbral_dinamico(cuenta.transacciones)

            guardar_gasto = True

            if umbral > 0 and gasto.importe > umbral:
                print('¡ANOMALÍA!')
                print(f'El gasto "{gasto.concepto}" de {gasto.importe} es inusualmente alto.')

                respuesta = input("¿Estás seguro de que quieres añadir este gasto tan alto? (s/n): ")

                if respuesta.lower() != "s":
                    guardar_gasto = False

            if guardar_gasto:
                cuenta.agregar_transaccion(gasto)
                print("Gasto añadido correctamente")
            else:
                print("Operación cancelada. El gasto no se ha guardado.")

        elif opcion == "3":
            cuenta.mostrar()

        elif opcion == "4":
            print(f"\nSaldo actual: {cuenta.saldo}€")

        elif opcion == "5":
            mes = input("Mes del presupuesto: ")
            while True:
                try:
                    cantidad = float(input("Cantidad presupuestada: "))
                    if cantidad <= 0:
                        raise ValueError
                    break
                except ValueError:
                    print("Introduce un importe válido (>0)")
            p = Presupuesto(mes, cantidad)
            presupuestos.append(p)
            print("Presupuesto creado")

        elif opcion == "6":
            if len(presupuestos) < 2:
                print("Necesitas al menos dos presupuestos para comparar")
            else:
                for i, p in enumerate(presupuestos):
                    print(f"{i + 1}. {p.mes}: {p.cantidad}€")
                idx1 = int(input("Elige el primer presupuesto: ")) - 1
                idx2 = int(input("Elige el segundo presupuesto: ")) - 1
                if 0 <= idx1 < len(presupuestos) and 0 <= idx2 < len(presupuestos):
                    print(
                        f"¿{presupuestos[idx1].mes} > {presupuestos[idx2].mes}? {presupuestos[idx1].comparar(presupuestos[idx2])}")
                else:
                    print("Selección inválida")

        elif opcion == "7":
            GestorArchivos.guardar_datos(cuenta)
            print("¡Hasta luego!")
            break

        elif opcion == "8":
            comparador = Comparador(cuenta)
            comparador.mostrar_comparativa()

        else:
            print("Opción no válida, intenta de nuevo")
