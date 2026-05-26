import csv
import os
import pickle
from datetime import datetime
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso
from GastoFijo import GastoFijo
from IngresoFijo import IngresoFijo
from Excepciones import ArchivoCorruptoError, ArchivoNoEncontradoError


class GestorArchivos:
    """Gestiona la persistencia de datos en CSV, TXT y backups Binarios."""

    CABECERAS = ["Tipo", "Concepto_o_Nombre", "Importe_o_Saldo", "Categoria", "Fecha", "Extra_Origen_o_Pago"]

    # ── [TEMA 11] Copias de Seguridad Binarias ───────────────────────────────

    @staticmethod
    def guardar_backup_binario(cuenta, directorio="backups"):
        if cuenta is None:
            return
        if not os.path.exists(directorio):
            os.mkdir(directorio)
        ruta = os.path.join(directorio, "seguridad.dat")
        try:
            with open(ruta, "wb") as archivo:
                pickle.dump(cuenta, archivo)
        except IOError as e:
            print(f"Error al guardar copia de seguridad: {e}")

    @staticmethod
    def recuperar_backup_binario(ruta="backups/seguridad.dat"):
        """Restaura la cuenta completa desde el archivo binario."""
        if not os.path.exists(ruta):
            raise ArchivoNoEncontradoError(ruta)
        try:
            with open(ruta, "rb") as archivo:
                cuenta = pickle.load(archivo)
                return cuenta
        except (IOError, pickle.UnpicklingError):
            raise ArchivoCorruptoError(ruta)

    # ── Guardar CSV ──────────────────────────────────────────────────────────

    @staticmethod
    def guardar_datos(cuenta, ruta_archivo="datos.csv"):
        if cuenta is None:
            raise ValueError("No se puede guardar una cuenta nula.")
        try:
            with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(GestorArchivos.CABECERAS)
                writer.writerow(["Cuenta", cuenta.nombre, cuenta.saldo, "", "", ""])
                for t in cuenta.transacciones:
                    if isinstance(t, GastoFijo):
                        writer.writerow(["GastoFijo", t.concepto, t.importe, t.categoria, t.fecha,
                                         f"{t.metodo_pago}|{t.frecuencia}"])
                    elif isinstance(t, IngresoFijo):
                        writer.writerow(["IngresoFijo", t.concepto, t.importe, t.categoria, t.fecha,
                                         f"{t.origen}|{t.frecuencia}"])
                    elif isinstance(t, Gasto):
                        writer.writerow(["Gasto", t.concepto, t.importe, t.categoria, t.fecha, t.metodo_pago])
                    elif isinstance(t, Ingreso):
                        writer.writerow(["Ingreso", t.concepto, t.importe, t.categoria, t.fecha, t.origen])
        except IOError:
            raise IOError(f"No se pudo escribir en el archivo {ruta_archivo}")

    # ── Cargar CSV ───────────────────────────────────────────────────────────

    @staticmethod
    def cargar_datos(ruta_archivo="datos.csv"):
        """
        Carga la cuenta y sus transacciones desde un archivo CSV.
        Devuelve un objeto Cuenta, o None si el archivo no existe todavia.

        :raises ArchivoCorruptoError: Si el archivo tiene un formato irreconocible.
        """
        if not os.path.exists(ruta_archivo):
            return None  # Primera ejecucion: no hay datos todavia

        try:
            with open(ruta_archivo, mode='r', newline='', encoding='utf-8') as archivo:
                reader = csv.reader(archivo)

                # Saltar la fila de cabeceras
                try:
                    next(reader)
                except StopIteration:
                    raise ArchivoCorruptoError(ruta_archivo)

                # Primera fila de datos: la cuenta
                try:
                    fila_cuenta = next(reader)
                except StopIteration:
                    raise ArchivoCorruptoError(ruta_archivo)

                if not fila_cuenta or fila_cuenta[0] != "Cuenta":
                    raise ArchivoCorruptoError(ruta_archivo)

                nombre_cuenta  = fila_cuenta[1]
                saldo_guardado = float(fila_cuenta[2])

                # Creamos la cuenta con saldo 0 para que agregar_transaccion
                # no duplique el saldo; al final lo restauramos al valor exacto guardado
                cuenta = Cuenta(nombre_cuenta, saldo_inicial=0.0)

                # Leer transacciones fila a fila
                for fila in reader:
                    if len(fila) < 6:
                        continue  # Fila incompleta, la ignoramos

                    tipo, concepto, importe_str, categoria, fecha, extra = fila

                    try:
                        importe = float(importe_str)
                    except ValueError:
                        continue  # Importe corrupto, saltamos esta fila

                    try:
                        if tipo == "GastoFijo":
                            partes     = extra.split("|", 1)
                            metodo_pago = partes[0]
                            frecuencia  = partes[1] if len(partes) > 1 else "Mensual"
                            t = GastoFijo(concepto, importe, categoria, fecha, metodo_pago, frecuencia)

                        elif tipo == "IngresoFijo":
                            partes     = extra.split("|", 1)
                            origen     = partes[0]
                            frecuencia = partes[1] if len(partes) > 1 else "Mensual"
                            t = IngresoFijo(concepto, importe, categoria, fecha, origen, frecuencia)

                        elif tipo == "Gasto":
                            t = Gasto(concepto, importe, categoria, fecha, extra)

                        elif tipo == "Ingreso":
                            t = Ingreso(concepto, importe, categoria, fecha, extra)

                        else:
                            continue  # Tipo desconocido, lo ignoramos

                        # Insertamos directamente en la lista para no tocar el saldo
                        cuenta.transacciones.append(t)

                    except Exception:
                        continue  # Si una fila falla por cualquier razon, seguimos

                # Restauramos el saldo exacto que tenia la cuenta al guardarse
                cuenta.saldo = saldo_guardado
                return cuenta

        except (IOError, csv.Error):
            raise ArchivoCorruptoError(ruta_archivo)

    # ── Exportar informe TXT ─────────────────────────────────────────────────

    @staticmethod
    def exportar_informe_txt(cuenta, ruta_archivo="informe.txt"):
        """
        Exporta un informe legible de la cuenta a un archivo .txt.

        :raises IOError: Si no se puede escribir el archivo.
        """
        if cuenta is None:
            raise ValueError("No se puede exportar una cuenta nula.")

        try:
            total_ingresos, total_gastos, diferencia = cuenta.balance_ingresos_gastos()
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            with open(ruta_archivo, mode='w', encoding='utf-8') as f:
                f.write("=" * 55 + "\n")
                f.write(f"  INFORME DE CUENTA: {cuenta.nombre}\n")
                f.write(f"  Generado el: {ahora}\n")
                f.write("=" * 55 + "\n\n")
                f.write(f"  Saldo actual:        {cuenta.saldo:>10.2f} EUR\n")
                f.write(f"  Total ingresos:      {total_ingresos:>10.2f} EUR\n")
                f.write(f"  Total gastos:        {total_gastos:>10.2f} EUR\n")
                f.write(f"  Diferencia neta:     {diferencia:>10.2f} EUR\n")
                f.write(f"  Num transacciones:   {len(cuenta):>10}\n")
                f.write("\n" + "-" * 55 + "\n")
                f.write("  DETALLE DE TRANSACCIONES\n")
                f.write("-" * 55 + "\n\n")

                if not cuenta.transacciones:
                    f.write("  (Sin movimientos registrados)\n")
                else:
                    for t in cuenta.transacciones:
                        f.write(f"  {t.mostrar()}\n")

                f.write("\n" + "=" * 55 + "\n")

        except IOError as e:
            raise IOError(f"No se pudo escribir el informe en '{ruta_archivo}': {e}")
