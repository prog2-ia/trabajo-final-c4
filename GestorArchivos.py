import csv
import os
from datetime import datetime
from Cuenta import Cuenta
from Gasto import Gasto
from Ingreso import Ingreso
from GastoFijo import GastoFijo
from IngresoFijo import IngresoFijo
from Excepciones import ArchivoCorruptoError, ArchivoNoEncontradoError


class GestorArchivos:
    """Gestiona la persistencia de datos en CSV y la exportación a TXT."""

    CABECERAS = ["Tipo", "Concepto_o_Nombre", "Importe_o_Saldo", "Categoria", "Fecha", "Extra_Origen_o_Pago"]

    # ── Guardar ──────────────────────────────────────────────────────────────

    @staticmethod
    def guardar_datos(cuenta, ruta_archivo="datos.csv"):
        """
        Serializa la cuenta y todas sus transacciones en un CSV.

        :raises IOError: Si no se puede escribir el archivo.
        """
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

            print(f"\n✔  Datos guardados en '{ruta_archivo}'")

        except OSError as e:
            raise IOError(f"No se pudo escribir el archivo '{ruta_archivo}': {e}")

    # ── Cargar ───────────────────────────────────────────────────────────────

    @staticmethod
    def cargar_datos(ruta_archivo="datos.csv"):
        """
        Lee el CSV y reconstruye la cuenta con todas sus transacciones.

        :returns: Objeto Cuenta, o None si el archivo no existe.
        :raises ArchivoCorruptoError: Si el archivo existe pero no puede leerse correctamente.
        """
        if not os.path.exists(ruta_archivo):
            return None

        cuenta = None

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
                reader = csv.reader(archivo)
                next(reader, None)  # Saltar cabecera

                for numero_fila, fila in enumerate(reader, start=2):
                    if not fila or not fila[0].strip():
                        continue

                    try:
                        tipo = fila[0].strip()

                        if tipo == "Cuenta":
                            cuenta = Cuenta(fila[1])
                            cuenta.saldo = float(fila[2])

                        elif cuenta is None:
                            # Si encontramos transacciones antes de la cuenta, el archivo está mal
                            raise ArchivoCorruptoError(ruta_archivo)

                        elif tipo == "IngresoFijo":
                            partes = fila[5].split('|')
                            ing_f = IngresoFijo(fila[1], float(fila[2]), fila[3], fila[4],
                                                partes[0], partes[1] if len(partes) > 1 else "Mensual")
                            cuenta.transacciones.append(ing_f)

                        elif tipo == "GastoFijo":
                            partes = fila[5].split('|')
                            gas_f = GastoFijo(fila[1], float(fila[2]), fila[3], fila[4],
                                              partes[0], partes[1] if len(partes) > 1 else "Mensual")
                            cuenta.transacciones.append(gas_f)

                        elif tipo == "Gasto":
                            cuenta.transacciones.append(
                                Gasto(fila[1], float(fila[2]), fila[3], fila[4], fila[5])
                            )

                        elif tipo == "Ingreso":
                            cuenta.transacciones.append(
                                Ingreso(fila[1], float(fila[2]), fila[3], fila[4], fila[5])
                            )

                    except (ValueError, IndexError):
                        print(f"  ⚠  Fila {numero_fila} ignorada por datos incorrectos.")
                        continue

        except ArchivoCorruptoError:
            raise
        except Exception as e:
            raise ArchivoCorruptoError(ruta_archivo) from e

        return cuenta

    # ── Exportar a TXT ───────────────────────────────────────────────────────

    @staticmethod
    def exportar_informe_txt(cuenta, ruta_archivo="informe.txt"):
        """
        Genera un informe de texto legible con el resumen completo de la cuenta.

        :raises IOError: Si no se puede crear el archivo.
        """
        if cuenta is None:
            raise ValueError("No se puede exportar una cuenta nula.")

        try:
            from Ingreso import Ingreso

            total_ingresos = sum(t.importe for t in cuenta.transacciones if isinstance(t, Ingreso))
            total_gastos = sum(t.importe for t in cuenta.transacciones if not isinstance(t, Ingreso))

            lineas = [
                "=" * 50,
                f"  INFORME FINANCIERO — {cuenta.nombre}",
                f"  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                "=" * 50,
                f"  Saldo actual:    {cuenta.saldo:.2f}€",
                f"  Total ingresos:  {total_ingresos:.2f}€",
                f"  Total gastos:    {total_gastos:.2f}€",
                f"  Diferencia neta: {total_ingresos - total_gastos:.2f}€",
                f"  Nº transacciones: {len(cuenta.transacciones)}",
                "─" * 50,
                "  DETALLE DE TRANSACCIONES",
                "─" * 50,
            ]

            for t in cuenta.transacciones:
                lineas.append(f"  {t.mostrar()}")

            lineas += [
                "─" * 50,
                "  GASTOS POR CATEGORÍA",
                "─" * 50,
            ]

            categorias = cuenta.obtener_gastos_por_categoria()
            if categorias:
                total_cat = sum(categorias.values())
                for cat, monto in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                    pct = (monto / total_cat) * 100
                    lineas.append(f"  {cat:<20} {monto:>8.2f}€  ({pct:.1f}%)")
            else:
                lineas.append("  Sin gastos registrados.")

            lineas.append("=" * 50)

            with open(ruta_archivo, mode='w', encoding='utf-8') as f:
                f.write("\n".join(lineas))

            print(f"\n✔  Informe exportado en '{ruta_archivo}'")

        except OSError as e:
            raise IOError(f"No se pudo crear el informe '{ruta_archivo}': {e}")
