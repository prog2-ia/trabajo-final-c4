"""
GESTOR DE FINANZAS PERSONALES  v4.0
Alejandro Garcia Plo  &  Alex Soler Barcelo
"""

import os
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
    PresupuestoInvalidoError,
    PresupuestoDuplicadoError,
    TransaccionNoEncontradaError,
    SaldoInsuficienteError,
    ArchivoCorruptoError,
)

# ─────────────────────────────────────────────────────────────
#   CONSTANTES DE DISEÑO
# ─────────────────────────────────────────────────────────────

ANCHO = 56

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

# ─────────────────────────────────────────────────────────────
#   UTILIDADES DE IMPRESION
# ─────────────────────────────────────────────────────────────

def cabecera_pantalla(nombre, cuenta=None):
    limpiar()
    print()
    print("  +" + "=" * (ANCHO - 2) + "+")
    print(f"  |{'GESTOR DE FINANZAS  v4.0':^{ANCHO}}|")
    print("  +" + "=" * (ANCHO - 2) + "+")
    if cuenta:
        saldo  = cuenta.saldo
        signo  = "+" if saldo >= 0 else ""
        linea1 = f" Titular: {cuenta.nombre}"
        linea2 = f" Saldo: {signo}{saldo:.2f}EUR  |  Mov: {len(cuenta.transacciones)}  |  {datetime.today().strftime('%d/%m/%Y')}"
        print(f"  |{linea1:<{ANCHO}}|")
        print(f"  |{linea2:<{ANCHO}}|")
        print("  +" + "-" * (ANCHO - 2) + "+")
    print(f"  |{(' ' + nombre):^{ANCHO}}|")
    print("  +" + "=" * (ANCHO - 2) + "+")
    print()


def seccion(titulo):
    relleno = ANCHO - len(titulo) - 6
    print(f"\n  .[ {titulo} ]{'.' * max(1, relleno)}")


def ok(msg):    print(f"\n  [  OK  ]  {msg}")
def error(msg): print(f"\n  [ FALLO]  {msg}")
def aviso(msg): print(f"\n  [  >>  ]  {msg}")

def confirmar(pregunta):
    r = input(f"\n  [ ?? ]  {pregunta} (s/n): ").strip().lower()
    return r == 's'

def pausar():
    input("\n  [ Pulsa ENTER para continuar... ]")


# ─────────────────────────────────────────────────────────────
#   ENTRADAS DE USUARIO
# ─────────────────────────────────────────────────────────────

def pedir_importe(mensaje="  Importe (EUR): "):
    while True:
        try:
            raw   = input(mensaje).strip().replace(",", ".")
            valor = float(raw)
            if valor <= 0:
                raise ImporteInvalidoError(valor)
            return valor
        except ImporteInvalidoError as e:
            error(e)
        except ValueError:
            error("Introduce un numero valido (ej. 12.50).")


def pedir_fecha(mensaje="  Fecha DD/MM/AAAA [ENTER=hoy]: "):
    while True:
        entrada = input(mensaje).strip()
        if entrada == "":
            return datetime.today().strftime("%d/%m/%Y")
        try:
            datetime.strptime(entrada, "%d/%m/%Y")
            return entrada
        except ValueError:
            error("Formato incorrecto. Usa DD/MM/AAAA (ej. 23/05/2025).")


def pedir_texto(mensaje, campo="campo"):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        error(f"El {campo} no puede estar vacio.")


def pedir_opcion_lista(lista, campo="opcion"):
    for i, item in enumerate(lista, 1):
        print(f"    {i:>2}.  {item}")
    while True:
        try:
            idx = int(input(f"\n  Selecciona {campo} (numero): ")) - 1
            if 0 <= idx < len(lista):
                return idx
            error(f"Elige entre 1 y {len(lista)}.")
        except ValueError:
            error("Introduce un numero entero.")


# ─────────────────────────────────────────────────────────────
#   PANTALLA DE BIENVENIDA E INICIO DE SESION
# ─────────────────────────────────────────────────────────────

def pantalla_bienvenida():
    limpiar()
    print()
    print("  +" + "=" * (ANCHO - 2) + "+")
    print(f"  |{'':^{ANCHO}}|")
    print(f"  |{'G E S T O R   D E   F I N A N Z A S':^{ANCHO}}|")
    print(f"  |{'v 4 . 0':^{ANCHO}}|")
    print(f"  |{'':^{ANCHO}}|")
    print("  +" + "=" * (ANCHO - 2) + "+")
    print(f"  |{'Alejandro Garcia Plo  &  Alex Soler Barcelo':^{ANCHO}}|")
    print("  +" + "-" * (ANCHO - 2) + "+")
    print()


def iniciar_sesion():
    pantalla_bienvenida()
    cuenta = None

    try:
        cuenta = GestorArchivos.cargar_datos()
    except ArchivoCorruptoError as e:
        error(f"Archivo danado: {e}")
        aviso("Se creara una cuenta nueva.")
        pausar()
        pantalla_bienvenida()

    if cuenta is not None:
        print(f"  Sesion encontrada:")
        print(f"  +{'-' * (ANCHO - 2)}+")
        print(f"  |  {'Titular':<20} {cuenta.nombre:<{ANCHO - 25}}|")
        print(f"  |  {'Saldo guardado':<20} {cuenta.saldo:.2f} EUR{'':<{ANCHO - 32}}|")
        print(f"  |  {'Transacciones':<20} {len(cuenta.transacciones):<{ANCHO - 25}}|")
        print(f"  +{'-' * (ANCHO - 2)}+")
        print()
        if confirmar("Cargar esta sesion"):
            ok("Sesion cargada correctamente.")
            pausar()
            return cuenta
        aviso("Se creara una cuenta nueva.")
        print()

    # Cuenta nueva
    seccion("NUEVA CUENTA")
    print()
    nombre = pedir_texto("  Nombre del titular : ", "nombre")
    saldo  = pedir_importe("  Saldo inicial (EUR): ")
    nueva  = Cuenta(nombre)
    nueva.saldo = saldo
    ok(f"Cuenta '{nombre}' creada con {saldo:.2f}EUR de saldo inicial.")
    pausar()
    return nueva


# ─────────────────────────────────────────────────────────────
#   MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("1",  "Registrar ingreso",              "MOVIMIENTOS"),
    ("2",  "Registrar gasto",                "MOVIMIENTOS"),
    ("3",  "Ver todas las transacciones",    "MOVIMIENTOS"),
    ("4",  "Ver saldo y balance",            "MOVIMIENTOS"),
    ("5",  "Buscar transaccion",             "MOVIMIENTOS"),
    ("6",  "Eliminar transaccion",           "MOVIMIENTOS"),
    ("7",  "Buscar por rango de fechas",     "MOVIMIENTOS"),
    ("8",  "Crear presupuesto mensual",      "PRESUPUESTOS"),
    ("9",  "Ver estado de presupuesto",      "PRESUPUESTOS"),
    ("10", "Comparar dos presupuestos",      "PRESUPUESTOS"),
    ("11", "Comparativa mensual historica",  "ANALISIS"),
    ("12", "Informe de anomalias",           "ANALISIS"),
    ("13", "Resumen detallado + categorias", "ANALISIS"),
    ("14", "Exportar informe a TXT",         "ARCHIVOS"),
    ("0",  "Guardar y salir",                "SISTEMA"),
]


def mostrar_menu(cuenta):
    cabecera_pantalla("MENU PRINCIPAL", cuenta)
    grupo_actual = ""
    col_cod  = 4
    col_item = ANCHO - col_cod - 4

    for codigo, etiqueta, grupo in MENU_ITEMS:
        if grupo != grupo_actual:
            grupo_actual = grupo
            pad = ANCHO - len(grupo) - 5
            print(f"  +-[ {grupo} ]{'-' * pad}+")
        print(f"  | {codigo:>2}.  {etiqueta:<{col_item}}|")

    print(f"  +{'-' * (ANCHO - 2)}+")
    print()


# ─────────────────────────────────────────────────────────────
#   ACCIONES
# ─────────────────────────────────────────────────────────────

def accion_agregar_transaccion(cuenta, detector, tipo):
    es_ingreso = (tipo == "ingreso")
    label      = "INGRESO" if es_ingreso else "GASTO"
    cabecera_pantalla(f"NUEVO {label}", cuenta)

    concepto  = pedir_texto("  Concepto           : ", "concepto")
    importe   = pedir_importe("  Importe (EUR)      : ")
    categoria = pedir_texto("  Categoria          : ", "categoria")
    fecha     = pedir_fecha("  Fecha [ENTER=hoy]  : ")

    # Alerta de anomalia antes de pedir el resto
    if not es_ingreso:
        umbral = detector.calcular_umbral_dinamico(cuenta.transacciones)
        if umbral > 0 and importe > umbral:
            print()
            print(f"  +{'!' * (ANCHO - 2)}+")
            print(f"  ! {'ALERTA  --  Gasto elevado detectado':^{ANCHO - 2}}!")
            print(f"  ! Importe: {importe:.2f}EUR   Umbral: {umbral:.2f}EUR{'':{ANCHO - 42}}!")
            print(f"  +{'!' * (ANCHO - 2)}+")
            if not confirmar("Continuar con el registro de todas formas"):
                aviso("Operacion cancelada.")
                pausar()
                return

    print()
    if es_ingreso:
        origen  = pedir_texto("  Origen (ej. Nomina): ", "origen")
        es_fijo = confirmar("Es un ingreso fijo/recurrente")
        if es_fijo:
            print("    Opciones: Mensual / Semanal / Anual")
            frecuencia = input("  Frecuencia          : ").strip() or "Mensual"
            t = IngresoFijo(concepto, importe, categoria, fecha, origen, frecuencia)
        else:
            t = Ingreso(concepto, importe, categoria, fecha, origen)
    else:
        metodo  = pedir_texto("  Metodo pago        : ", "metodo")
        es_fijo = confirmar("Es un gasto fijo/recurrente")
        if es_fijo:
            print("    Opciones: Mensual / Anual")
            frecuencia = input("  Frecuencia          : ").strip() or "Mensual"
            t = GastoFijo(concepto, importe, categoria, fecha, metodo, frecuencia)
        else:
            t = Gasto(concepto, importe, categoria, fecha, metodo)

    # Resumen de confirmacion
    print()
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  | {'RESUMEN DE LA OPERACION':^{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  |  {'Tipo':<18} {t.__class__.__name__:<{ANCHO - 23}}|")
    print(f"  |  {'Concepto':<18} {t.concepto:<{ANCHO - 23}}|")
    print(f"  |  {'Importe':<18} {t.importe:.2f} EUR{'':<{ANCHO - 30}}|")
    print(f"  |  {'Categoria':<18} {t.categoria:<{ANCHO - 23}}|")
    print(f"  |  {'Fecha':<18} {t.fecha:<{ANCHO - 23}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")

    if confirmar("Confirmar y registrar"):
        try:
            cuenta.agregar_transaccion(t)
            ok(f"Registrado.  Nuevo saldo --> {cuenta.saldo:.2f}EUR")
        except SaldoInsuficienteError as e:
            error(e)
    else:
        aviso("Operacion cancelada.")

    pausar()


def accion_ver_transacciones(cuenta):
    cabecera_pantalla("TODAS LAS TRANSACCIONES", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones registradas todavia.")
        pausar()
        return

    print("  Filtrar por tipo:")
    print("    1.  Todas")
    print("    2.  Solo ingresos")
    print("    3.  Solo gastos")
    filtro = input("\n  Opcion [ENTER=todas]: ").strip()

    if filtro == "2":
        lista = [t for t in cuenta.transacciones if isinstance(t, Ingreso)]
        etiq  = "INGRESOS"
    elif filtro == "3":
        lista = [t for t in cuenta.transacciones if not isinstance(t, Ingreso)]
        etiq  = "GASTOS"
    else:
        lista = cuenta.transacciones
        etiq  = "TODAS"

    print()
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  | {etiq + '  (' + str(len(lista)) + ' movimientos)':<{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    for t in lista:
        print(f"  | {t.mostrar():<{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    total = sum(t.importe for t in lista)
    print(f"  |  {'Total mostrado:':<20} {total:.2f} EUR{'':<{ANCHO - 28}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")

    if filtro != "2":
        print()
        cuenta.mostrar_reporte_categorias()

    pausar()


def accion_ver_saldo(cuenta):
    cabecera_pantalla("SALDO Y BALANCE", cuenta)
    total_ing, total_gas, dif = cuenta.balance_ingresos_gastos()
    estado = "SUPERAVIT" if dif >= 0 else "DEFICIT"
    signo  = "+" if dif >= 0 else ""

    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  | {'RESUMEN FINANCIERO':^{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  |  {'Saldo actual':<24} {cuenta.saldo:>10.2f} EUR{'':<6}|")
    print(f"  |  {'-' * (ANCHO - 6)}  |")
    print(f"  |  {'Total ingresos':<24} {total_ing:>10.2f} EUR{'':<6}|")
    print(f"  |  {'Total gastos':<24} {total_gas:>10.2f} EUR{'':<6}|")
    print(f"  |  {'-' * (ANCHO - 6)}  |")
    label_bal = f"Balance neto  ({estado})"
    print(f"  |  {label_bal:<24} {signo}{dif:.2f} EUR{'':<{ANCHO - len(label_bal) - len(f'{signo}{dif:.2f}') - 11}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")

    # Histograma de gastos por mes
    try:
        datos = Comparador(cuenta).obtener_gastos_por_mes()
        if datos:
            seccion("GASTOS POR MES")
            max_val = max(datos.values())
            for mes, val in datos.items():
                bar_len = int((val / max_val) * 22) if max_val > 0 else 0
                barra   = "#" * bar_len
                print(f"  {mes}  [{barra:<22}]  {val:.2f}EUR")
    except (ValueError, Exception):
        pass

    pausar()


def accion_buscar(cuenta):
    cabecera_pantalla("BUSCAR TRANSACCION", cuenta)
    termino = pedir_texto("  Concepto a buscar: ", "termino")
    try:
        resultados = cuenta.buscar_por_concepto(termino)
        print()
        print(f"  +{'-' * (ANCHO - 2)}+")
        print(f"  | {str(len(resultados)) + ' resultado(s) para: ' + termino:<{ANCHO - 2}}|")
        print(f"  +{'-' * (ANCHO - 2)}+")
        for t in resultados:
            print(f"  | >> {t.mostrar():<{ANCHO - 6}}|")
        print(f"  +{'-' * (ANCHO - 2)}+")
    except TransaccionNoEncontradaError as e:
        error(e)
    pausar()


def accion_eliminar(cuenta):
    cabecera_pantalla("ELIMINAR TRANSACCION", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones para eliminar.")
        pausar()
        return

    termino = pedir_texto("  Concepto a eliminar: ", "concepto")

    try:
        resultados = cuenta.buscar_por_concepto(termino)
    except TransaccionNoEncontradaError as e:
        error(e)
        pausar()
        return

    print()
    print(f"  Se encontraron {len(resultados)} coincidencia(s):")
    print(f"  +{'-' * (ANCHO - 2)}+")
    for t in resultados:
        print(f"  | {t.mostrar():<{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")

    if not confirmar("Eliminar la primera coincidencia"):
        aviso("Operacion cancelada.")
        pausar()
        return

    try:
        eliminada = resultados[0]
        cuenta.eliminar_transaccion(eliminada.concepto)
        ok(f"'{eliminada.concepto}' eliminada.  Saldo: {cuenta.saldo:.2f}EUR")
    except (TransaccionNoEncontradaError, FinanzasError) as e:
        error(e)

    pausar()


def accion_buscar_rango_fechas(cuenta):
    cabecera_pantalla("BUSCAR POR RANGO DE FECHAS", cuenta)
    print("  Introduce el periodo que deseas consultar.")
    print()
    fecha_ini = pedir_fecha("  Fecha inicio [ENTER=hoy]: ")
    fecha_fin = pedir_fecha("  Fecha fin    [ENTER=hoy]: ")

    try:
        resultados = cuenta.buscar_por_rango_fechas(fecha_ini, fecha_fin)
        total = sum(t.importe for t in resultados)
        print()
        print(f"  +{'-' * (ANCHO - 2)}+")
        encabezado = f" {len(resultados)} transaccion(es)  {fecha_ini} -- {fecha_fin}"
        print(f"  |{encabezado:<{ANCHO - 2}}|")
        print(f"  +{'-' * (ANCHO - 2)}+")
        for t in resultados:
            print(f"  | {t.mostrar():<{ANCHO - 2}}|")
        print(f"  +{'-' * (ANCHO - 2)}+")
        print(f"  |  {'Suma total:':<20} {total:.2f} EUR{'':<{ANCHO - 28}}|")
        print(f"  +{'-' * (ANCHO - 2)}+")
    except (TransaccionNoEncontradaError, ValueError) as e:
        error(e)

    pausar()


def accion_crear_presupuesto(presupuestos):
    limpiar()
    cabecera_pantalla("NUEVO PRESUPUESTO MENSUAL")

    MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    print("  Selecciona el mes:\n")
    mes_idx = pedir_opcion_lista(MESES, "mes")
    mes     = MESES[mes_idx]

    if mes in presupuestos:
        aviso(f"Ya existe un presupuesto para {mes} ({presupuestos[mes].cantidad:.2f}EUR).")
        if not confirmar("Sobreescribir"):
            aviso("Operacion cancelada.")
            pausar()
            return

    monto = pedir_importe(f"\n  Cantidad presupuestada para {mes} (EUR): ")

    try:
        presupuestos[mes] = Presupuesto(mes, monto)
        ok(f"Presupuesto {mes}: {monto:.2f}EUR guardado.")
    except PresupuestoInvalidoError as e:
        error(e)

    pausar()


def accion_estado_presupuesto(cuenta, presupuestos):
    cabecera_pantalla("ESTADO DE PRESUPUESTO", cuenta)

    if not presupuestos:
        aviso("No hay presupuestos. Usa la opcion 8 para crear uno.")
        pausar()
        return

    print("  Selecciona el presupuesto a consultar:\n")
    lista_meses = list(presupuestos.keys())
    etiquetas   = [f"{m}  ({presupuestos[m].cantidad:.2f}EUR)" for m in lista_meses]
    idx = pedir_opcion_lista(etiquetas, "presupuesto")
    mes = lista_meses[idx]
    p   = presupuestos[mes]

    estado = p.estado_presupuesto(cuenta)
    pct    = min(estado["porcentaje_usado"], 100)
    bar_l  = int(pct / 4)
    barra  = "#" * bar_l + "." * (25 - bar_l)

    print()
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  | {'PRESUPUESTO  ' + mes.upper():^{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  |  {'Presupuestado':<22} {estado['presupuestado']:>10.2f} EUR{'':<5}|")
    print(f"  |  {'Gastado hasta hoy':<22} {estado['gastado']:>10.2f} EUR{'':<5}|")
    print(f"  |  {'Restante':<22} {estado['restante']:>10.2f} EUR{'':<5}|")
    print(f"  |  {'-' * (ANCHO - 6)}  |")
    barra_linea = f"  Uso: [{barra}] {estado['porcentaje_usado']:.1f}%"
    print(f"  |{barra_linea:<{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")

    if estado["en_superavit"]:
        ok(f"Dentro del presupuesto. Quedan {estado['restante']:.2f}EUR.")
    else:
        error(f"Presupuesto superado en {abs(estado['restante']):.2f}EUR.")

    pausar()


def accion_comparar_presupuestos(presupuestos):
    limpiar()
    cabecera_pantalla("COMPARAR PRESUPUESTOS")

    if len(presupuestos) < 2:
        aviso("Necesitas al menos 2 presupuestos para comparar.")
        pausar()
        return

    lista_p = list(presupuestos.values())
    etiq    = [f"{p.mes:<14}  {p.cantidad:.2f}EUR" for p in lista_p]

    print("  Selecciona el PRIMER presupuesto:\n")
    idx1 = pedir_opcion_lista(etiq)
    print()
    print("  Selecciona el SEGUNDO presupuesto:\n")
    idx2 = pedir_opcion_lista(etiq)

    p1, p2 = lista_p[idx1], lista_p[idx2]
    dif    = abs(p1.cantidad - p2.cantidad)
    mayor  = p1 if p1.comparar(p2) else p2
    menor  = p2 if p1.comparar(p2) else p1

    print()
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  | {'COMPARATIVA':^{ANCHO - 2}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  |  {p1.mes:<20} {p1.cantidad:>10.2f} EUR{'':<8}|")
    print(f"  |  {p2.mes:<20} {p2.cantidad:>10.2f} EUR{'':<8}|")
    print(f"  |  {'-' * (ANCHO - 6)}  |")
    print(f"  |  {'Diferencia':<20} {dif:>10.2f} EUR{'':<8}|")
    print(f"  |  {'Mayor':<20} {mayor.mes:<{ANCHO - 26}}|")
    if menor.cantidad > 0:
        variacion = ((mayor.cantidad - menor.cantidad) / menor.cantidad) * 100
        var_str   = f"+{variacion:.1f}% sobre {menor.mes}"
        print(f"  |  {'Variacion':<20} {var_str:<{ANCHO - 24}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")

    pausar()


def accion_comparativa_mensual(cuenta):
    cabecera_pantalla("COMPARATIVA MENSUAL HISTORICA", cuenta)
    Comparador(cuenta).mostrar_comparativa()
    pausar()


def accion_informe_anomalias(cuenta, detector):
    cabecera_pantalla("INFORME DE ANOMALIAS", cuenta)
    print()
    print(f"  Multiplicador  : x{detector.multiplicador}")
    print(f"  Muestra        : ultimos {detector.num_recientes} gastos")
    print()
    detector.informe_anomalias(cuenta.transacciones)
    pausar()


def accion_resumen_detallado(cuenta):
    cabecera_pantalla("RESUMEN DETALLADO", cuenta)
    cuenta.generar_resumen()
    cuenta.mostrar_reporte_categorias()
    pausar()


def accion_exportar_txt(cuenta):
    cabecera_pantalla("EXPORTAR INFORME A TXT", cuenta)
    print()
    nombre = input("  Nombre del archivo [ENTER = 'informe.txt']: ").strip()
    if not nombre:
        nombre = "informe.txt"
    if not nombre.endswith(".txt"):
        nombre += ".txt"
    try:
        GestorArchivos.exportar_informe_txt(cuenta, nombre)
        ok(f"Informe guardado como '{nombre}'.")
    except IOError as e:
        error(e)
    pausar()


def accion_guardar_salir(cuenta):
    cabecera_pantalla("GUARDAR Y SALIR", cuenta)
    print()
    print(f"  +{'-' * (ANCHO - 2)}+")
    print(f"  |  {'Titular':<20} {cuenta.nombre:<{ANCHO - 25}}|")
    print(f"  |  {'Saldo':<20} {cuenta.saldo:.2f} EUR{'':<{ANCHO - 32}}|")
    print(f"  |  {'Transacciones':<20} {len(cuenta.transacciones):<{ANCHO - 25}}|")
    print(f"  +{'-' * (ANCHO - 2)}+")
    print()
    if confirmar("Guardar y salir"):
        try:
            GestorArchivos.guardar_datos(cuenta)
            print()
            print(f"  +{'=' * (ANCHO - 2)}+")
            print(f"  |{'Datos guardados correctamente.':^{ANCHO}}|")
            print(f"  |{'Hasta pronto!':^{ANCHO}}|")
            print(f"  +{'=' * (ANCHO - 2)}+")
            print()
            return True
        except IOError as e:
            error(f"No se pudo guardar: {e}")
            if confirmar("Salir de todas formas sin guardar"):
                return True
    else:
        aviso("Volviendo al menu principal.")
        pausar()
    return False


# ─────────────────────────────────────────────────────────────
#   BUCLE PRINCIPAL
# ─────────────────────────────────────────────────────────────

def main():
    cuenta       = iniciar_sesion()
    detector     = DetectorAnomalias()
    presupuestos = {}

    ACCIONES = {
        "1":  lambda: accion_agregar_transaccion(cuenta, detector, "ingreso"),
        "2":  lambda: accion_agregar_transaccion(cuenta, detector, "gasto"),
        "3":  lambda: accion_ver_transacciones(cuenta),
        "4":  lambda: accion_ver_saldo(cuenta),
        "5":  lambda: accion_buscar(cuenta),
        "6":  lambda: accion_eliminar(cuenta),
        "7":  lambda: accion_buscar_rango_fechas(cuenta),
        "8":  lambda: accion_crear_presupuesto(presupuestos),
        "9":  lambda: accion_estado_presupuesto(cuenta, presupuestos),
        "10": lambda: accion_comparar_presupuestos(presupuestos),
        "11": lambda: accion_comparativa_mensual(cuenta),
        "12": lambda: accion_informe_anomalias(cuenta, detector),
        "13": lambda: accion_resumen_detallado(cuenta),
        "14": lambda: accion_exportar_txt(cuenta),
    }

    while True:
        mostrar_menu(cuenta)
        opcion = input("  >> Opcion: ").strip()

        if opcion == "0":
            if accion_guardar_salir(cuenta):
                break
        elif opcion in ACCIONES:
            try:
                ACCIONES[opcion]()
            except FinanzasError as e:
                error(e)
                pausar()
            except Exception as e:
                error(f"Error inesperado: {e}")
                pausar()
        else:
            error("Opcion no valida. Elige entre 0 y 14.")
            pausar()


if __name__ == "__main__":
    main()