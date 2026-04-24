import csv
import os
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso
from GastoFijo import GastoFijo  # Nueva clase
from IngresoFijo import IngresoFijo  # Nueva clase


class GestorArchivos:

    @staticmethod
    def guardar_datos(cuenta, ruta_archivo="datos.csv"):
        with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)

            # 1. Cabeceras (mantenemos la estructura original)
            writer.writerow(
                ["Tipo", "Concepto_o_Nombre", "Importe_o_Saldo", "Categoria", "Fecha", "Extra_Origen_o_Pago"])

            # 2. Datos de la cuenta
            writer.writerow(["Cuenta", cuenta.nombre, cuenta.saldo, "", "", ""])

            # 3. Iteramos por todas las transacciones
            for t in cuenta.transacciones:
                if isinstance(t, GastoFijo):
                    # Guardamos pago y frecuencia juntos
                    extra = f"{t.metodo_pago}|{t.frecuencia}"
                    writer.writerow(["GastoFijo", t.concepto, t.importe, t.categoria, t.fecha, extra])

                elif isinstance(t, IngresoFijo):
                    # Guardamos origen y frecuencia juntos
                    extra = f"{t.origen}|{t.frecuencia}"
                    writer.writerow(["IngresoFijo", t.concepto, t.importe, t.categoria, t.fecha, extra])

                elif isinstance(t, Gasto):
                    writer.writerow(["Gasto", t.concepto, t.importe, t.categoria, t.fecha, t.metodo_pago])

                elif isinstance(t, Ingreso):
                    writer.writerow(["Ingreso", t.concepto, t.importe, t.categoria, t.fecha, t.origen])

        print(f"\n¡Datos guardados correctamente en {ruta_archivo}!")

    @staticmethod
    def cargar_datos(ruta_archivo="datos.csv"):
        """Lee el archivo CSV y reconstruye la cuenta y las transacciones."""
        if not os.path.exists(ruta_archivo):
            return None

        cuenta = None

        with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
            reader = csv.reader(archivo)
            next(reader, None)  # Saltar cabecera

            for fila in reader:
                if not fila:
                    continue

                tipo = fila[0]

                # Reconstrucción de la Cuenta
                if tipo == "Cuenta":
                    cuenta = Cuenta(fila[1])
                    cuenta.saldo = float(fila[2])

                # Reconstrucción de Ingresos Fijos
                elif tipo == "IngresoFijo" and cuenta is not None:
                    extra_data = fila[5].split('|')
                    origen = extra_data[0]
                    frecuencia = extra_data[1] if len(extra_data) > 1 else "Mensual"
                    ing_f = IngresoFijo(fila[1], float(fila[2]), fila[3], fila[4], origen, frecuencia)
                    cuenta.transacciones.append(ing_f)

                # Reconstrucción de Gastos Fijos
                elif tipo == "GastoFijo" and cuenta is not None:
                    extra_data = fila[5].split('|')
                    metodo_pago = extra_data[0]
                    frecuencia = extra_data[1] if len(extra_data) > 1 else "Mensual"
                    gas_f = GastoFijo(fila[1], float(fila[2]), fila[3], fila[4], metodo_pago, frecuencia)
                    cuenta.transacciones.append(gas_f)

                # Reconstrucción de Gastos normales
                elif tipo == "Gasto" and cuenta is not None:
                    gasto = Gasto(fila[1], float(fila[2]), fila[3], fila[4], fila[5])
                    cuenta.transacciones.append(gasto)

                # Reconstrucción de Ingresos normales
                elif tipo == "Ingreso" and cuenta is not None:
                    ingreso = Ingreso(fila[1], float(fila[2]), fila[3], fila[4], fila[5])
                    cuenta.transacciones.append(ingreso)

        return cuenta