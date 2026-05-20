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

        # Comprueba si existe la carpeta 'backups', si no, la crea (TEMA 11)
        if not os.path.exists(directorio):
            os.mkdir(directorio)

        ruta = os.path.join(directorio, "seguridad.dat")
        try:
            # Escribe en modo binario "wb"
            with open(ruta, "wb") as archivo:
                pickle.dump(cuenta, archivo)
        except IOError as e:
            print(f"Error al guardar copia de seguridad: {e}")

    @staticmethod
    def recuperar_backup_binario(ruta="backups/seguridad.dat"):
        """
        Restaura la cuenta completa desde el archivo binario.
        """
        if not os.path.exists(ruta):
            raise ArchivoNoEncontradoError(ruta)

        try:
            # Lee en modo binario "rb"
            with open(ruta, "rb") as archivo:
                cuenta = pickle.load(archivo)
                return cuenta
        except (IOError, pickle.UnpicklingError):
            raise ArchivoCorruptoError(ruta)

    # ── Guardar y Cargar CSV clásico (Vuestro código original) ───────────────

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
                        writer.writerow(
                            ["IngresoFijo", t.concepto, t.importe, t.categoria, t.fecha, f"{t.origen}|{t.frecuencia}"])
                    elif isinstance(t, Gasto):
                        writer.writerow(["Gasto", t.concepto, t.importe, t.categoria, t.fecha, t.metodo_pago])
                    elif isinstance(t, Ingreso):
                        writer.writerow(["Ingreso", t.concepto, t.importe, t.categoria, t.fecha, t.origen])
        except IOError:
            raise IOError(f"No se pudo escribir en el archivo {ruta_archivo}")

    @staticmethod
    def cargar_datos(ruta_archivo="datos.csv"):
        # Vuestro código original de cargar_datos...
        # (Cópialo aquí tal cual lo teníais, no he tocado esta parte para que el CSV siga funcionando igual)
        pass