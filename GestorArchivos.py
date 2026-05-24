import csv
import json
import os
import pickle
from datetime import datetime

from Cuenta import Cuenta
from Gasto import Gasto
from GastoFijo import GastoFijo
from Ingreso import Ingreso
from IngresoFijo import IngresoFijo
from Presupuesto import Presupuesto
from Excepciones import ArchivoCorruptoError, ArchivoNoEncontradoError


class GestorArchivos:
    """Gestiona la persistencia de datos en CSV, TXT y backups binarios."""

    CABECERAS = ["Tipo", "Concepto_o_Nombre", "Importe_o_Saldo", "Categoria", "Fecha", "Extra_Origen_o_Pago"]
    RUTA_PRESUPUESTOS = "presupuestos.json"

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

    # ── Presupuestos (JSON) ──────────────────────────────────────────────────

    @staticmethod
    def guardar_presupuestos(presupuestos, ruta=None):
        """
        Serializa el dict {mes: Presupuesto} en un archivo JSON.

        :param presupuestos: Dict con los presupuestos activos.
        :param ruta: Ruta del archivo (por defecto 'presupuestos.json').
        """
        if ruta is None:
            ruta = GestorArchivos.RUTA_PRESUPUESTOS
        datos = {mes: p.cantidad for mes, p in presupuestos.items()}
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error al guardar presupuestos: {e}")

    @staticmethod
    def cargar_presupuestos(ruta=None):
        """
        Carga el dict de presupuestos desde JSON.
        Devuelve {} si el archivo no existe o está dañado.
        """
        if ruta is None:
            ruta = GestorArchivos.RUTA_PRESUPUESTOS
        if not os.path.exists(ruta):
            return {}
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            return {mes: Presupuesto(mes, cantidad) for mes, cantidad in datos.items()}
        except (IOError, ValueError, KeyError):
            print("Aviso: no se pudieron recuperar los presupuestos guardados.")
            return {}

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
                        writer.writerow([
                            "GastoFijo", t.concepto, t.importe, t.categoria, t.fecha,
                            f"{t.metodo_pago}|{t.frecuencia}"
                        ])
                    elif isinstance(t, IngresoFijo):
                        writer.writerow([
                            "IngresoFijo", t.concepto, t.importe, t.categoria, t.fecha,
                            f"{t.origen}|{t.frecuencia}"
                        ])
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
        Carga la cuenta y sus transacciones desde un CSV.

        - Devuelve None si el archivo no existe (primera ejecución).
        - Lanza ArchivoCorruptoError si el formato no es reconocible.

        NOTA: Las transacciones se añaden directamente a la lista interna
        para evitar entradas duplicadas en el log de auditoría al cargar.
        """
        if not os.path.exists(ruta_archivo):
            return None

        cuenta = None
        saldo_guardado = 0.0

        try:
            with open(ruta_archivo, mode='r', newline='', encoding='utf-8') as archivo:
                reader = csv.reader(archivo)
                next(reader)  # saltar cabecera

                for fila in reader:
                    # Ignorar filas vacías o incompletas
                    if not fila or len(fila) < 6:
                        continue

                    tipo            = fila[0].strip()
                    nombre_concepto = fila[1].strip()
                    valor           = fila[2].strip()
                    categoria       = fila[3].strip()
                    fecha           = fila[4].strip()
                    extra           = fila[5].strip()

                    # ── Fila de cabecera de cuenta ──────────────────────────
                    if tipo == "Cuenta":
                        saldo_guardado = float(valor)
                        # Creamos con saldo 0; restauraremos el valor exacto al final
                        cuenta = Cuenta(nombre_concepto, 0.0)
                        continue

                    if cuenta is None:
                        raise ArchivoCorruptoError(ruta_archivo)

                    importe = float(valor)

                    # ── Construir la transacción según su tipo ──────────────
                    if tipo == "GastoFijo":
                        partes = extra.split('|', 1)
                        metodo = partes[0] if partes else "Otro"
                        frec   = partes[1] if len(partes) > 1 else "Mensual"
                        t = GastoFijo(nombre_concepto, importe, categoria, fecha, metodo, frec)

                    elif tipo == "IngresoFijo":
                        partes = extra.split('|', 1)
                        origen = partes[0] if partes else "Otro"
                        frec   = partes[1] if len(partes) > 1 else "Mensual"
                        t = IngresoFijo(nombre_concepto, importe, categoria, fecha, origen, frec)

                    elif tipo == "Gasto":
                        t = Gasto(nombre_concepto, importe, categoria, fecha, extra or "Otro")

                    elif tipo == "Ingreso":
                        t = Ingreso(nombre_concepto, importe, categoria, fecha, extra or "Otro")

                    else:
                        continue  # línea con tipo desconocido: la ignoramos

                    # Añadir directamente (sin auditoría) para no contaminar el log
                    cuenta.transacciones.append(t)

            if cuenta is not None:
                # Restaurar el saldo exacto que se guardó
                cuenta.saldo = saldo_guardado

        except (ValueError, IndexError):
            raise ArchivoCorruptoError(ruta_archivo)
        except IOError as e:
            raise IOError(f"No se pudo leer el archivo {ruta_archivo}: {e}")

        return cuenta

    # ── Exportar Informe a TXT ───────────────────────────────────────────────

    @staticmethod
    def exportar_informe_txt(cuenta, ruta_archivo="informe.txt"):
        """
        Genera un informe completo en texto plano con resumen, categorías
        y el historial de todas las transacciones.

        :raises IOError: Si no se puede escribir el archivo.
        """
        if cuenta is None:
            raise ValueError("No se puede exportar una cuenta nula.")

        total_ing, total_gas, dif = cuenta.balance_ingresos_gastos()
        ahora   = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sep_eq  = "=" * 55
        sep_gui = "-" * 55

        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:

                # ── Encabezado ──────────────────────────────────────────────
                f.write(f"{sep_eq}\n")
                f.write(f"  INFORME DE FINANZAS PERSONALES\n")
                f.write(f"  Titular : {cuenta.nombre}\n")
                f.write(f"  Generado: {ahora}\n")
                f.write(f"{sep_eq}\n\n")

                # ── Resumen numérico ────────────────────────────────────────
                estado = "SUPERAVIT" if dif >= 0 else "DEFICIT"
                f.write(f"  Saldo actual   : {cuenta.saldo:>10.2f} EUR\n")
                f.write(f"  Total ingresos : {total_ing:>10.2f} EUR\n")
                f.write(f"  Total gastos   : {total_gas:>10.2f} EUR\n")
                f.write(f"  Balance neto   : {dif:>10.2f} EUR  [{estado}]\n")
                f.write(f"  Transacciones  : {len(cuenta.transacciones):>10}\n\n")

                # ── Gastos por categoría ────────────────────────────────────
                gastos_cat = cuenta.obtener_gastos_por_categoria()
                if gastos_cat:
                    f.write(f"{sep_gui}\n")
                    f.write(f"  GASTOS POR CATEGORIA\n")
                    f.write(f"{sep_gui}\n")
                    for cat, monto in sorted(gastos_cat.items(), key=lambda x: x[1], reverse=True):
                        pct = (monto / total_gas * 100) if total_gas > 0 else 0
                        f.write(f"  {cat:<22} {monto:>10.2f} EUR  ({pct:5.1f}%)\n")
                    f.write(f"  {'TOTAL':<22} {total_gas:>10.2f} EUR\n\n")

                # ── Ingresos por categoría ──────────────────────────────────
                ing_cat = cuenta.obtener_ingresos_por_categoria()
                if ing_cat:
                    f.write(f"{sep_gui}\n")
                    f.write(f"  INGRESOS POR CATEGORIA\n")
                    f.write(f"{sep_gui}\n")
                    for cat, monto in sorted(ing_cat.items(), key=lambda x: x[1], reverse=True):
                        pct = (monto / total_ing * 100) if total_ing > 0 else 0
                        f.write(f"  {cat:<22} {monto:>10.2f} EUR  ({pct:5.1f}%)\n")
                    f.write(f"  {'TOTAL':<22} {total_ing:>10.2f} EUR\n\n")

                # ── Historial completo ──────────────────────────────────────
                f.write(f"{sep_gui}\n")
                f.write(f"  HISTORIAL COMPLETO DE TRANSACCIONES\n")
                f.write(f"{sep_gui}\n")
                if not cuenta.transacciones:
                    f.write("  (Sin movimientos registrados)\n")
                else:
                    for t in cuenta.transacciones:
                        f.write(f"  {t.mostrar()}\n")

                f.write(f"\n{sep_eq}\n")

        except IOError as e:
            raise IOError(f"No se pudo escribir en '{ruta_archivo}': {e}")