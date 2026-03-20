import csv
import os
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso


class GestorArchivos:

    @staticmethod
    def guardar_datos(cuenta, ruta_archivo="datos.csv"):
        with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as archivo:
            writer = csv.writer(archivo)

            # 1. Escribimos las cabeceras de las columnas
            writer.writerow(
                ["Tipo", "Concepto_o_Nombre", "Importe_o_Saldo", "Categoria", "Fecha", "Extra_Origen_o_Pago"])

            # 2. Escribimos los datos principales de la cuenta
            writer.writerow(["Cuenta", cuenta.nombre, cuenta.saldo, "", "", ""])

            # 3. Escribimos cada transacción
            for t in cuenta.transacciones:
                if isinstance(t, Gasto):
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
            next(reader, None)

            for fila in reader:
                if not fila:
                    continue

                tipo = fila[0]

                # Reconstruimos según el tipo que leemos en la primera columna
                if tipo == "Cuenta":
                    cuenta = Cuenta(fila[1])
                    cuenta.saldo = float(fila[2])
                elif tipo == "Gasto" and cuenta is not None:
                    gasto = Gasto(fila[1], float(fila[2]), fila[3], fila[4], fila[5])
                    cuenta.transacciones.append(gasto)
                elif tipo == "Ingreso" and cuenta is not None:
                    ingreso = Ingreso(fila[1], float(fila[2]), fila[3], fila[4], fila[5])
                    cuenta.transacciones.append(ingreso)

        return cuenta