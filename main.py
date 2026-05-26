"""
GESTOR DE FINANZAS PERSONALES
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
    PresupuestoInvalidoError,
    TransaccionNoEncontradaError,
    SaldoInsuficienteError,
    ArchivoCorruptoError,
)

# ─────────────────────────────────────────────────────────────
#   CONSTANTES
# ─────────────────────────────────────────────────────────────

ANCHO = 60

CATEGORIAS_GASTO   = ["Alimentacion", "Transporte", "Vivienda", "Salud",
                      "Ocio", "Ropa", "Tecnologia", "Educacion", "Otros"]
CATEGORIAS_INGRESO = ["Nomina", "Freelance", "Inversiones", "Regalo",
                      "Reembolso", "Otros"]
METODOS_PAGO       = ["Tarjeta debito", "Tarjeta credito", "Efectivo",
                      "Transferencia", "Bizum", "Otro"]
FRECUENCIAS        = ["Mensual", "Semanal", "Anual"]

# ─────────────────────────────────────────────────────────────
#   UTILIDADES DE PANTALLA
# ─────────────────────────────────────────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def linea(caracter="="):
    print("  +" + caracter * (ANCHO - 2) + "+")


def fila(texto, alineacion="<"):
    fmt = f"{texto:{alineacion}{ANCHO}}"
    print(f"  |{fmt}|")


def separador(caracter="-"):
    print(f"  +{caracter * (ANCHO - 2)}+")


def cabecera_pantalla(titulo, cuenta=None):
    limpiar()
    print()
    linea("=")
    fila("  GESTOR DE FINANZAS   ", "<")
    if cuenta:
        signo = "+" if cuenta.saldo >= 0 else ""
        fila(f"  {cuenta.nombre}  |  Saldo: {signo}{cuenta.saldo:.2f} EUR  |  {datetime.today().strftime('%d/%m/%Y')}", "<")
        separador("-")
    linea("=")
    fila(f"  {titulo}", "<")
    separador("-")
    print()


def seccion(titulo):
    pad = ANCHO - len(titulo) - 5
    print(f"\n  -- {titulo} {'-' * max(1, pad)}")


def ok(msg):    print(f"\n  [ OK ]  {msg}")
def error(msg): print(f"\n  [ERR ]  {msg}")
def aviso(msg): print(f"\n  [INFO]  {msg}")


def pausar():
    input("\n  Pulsa ENTER para continuar...")


def confirmar(pregunta):
    r = input(f"\n  {pregunta} (s/n): ").strip().lower()
    return r == "s"


# ─────────────────────────────────────────────────────────────
#   ENTRADAS DE USUARIO
# ─────────────────────────────────────────────────────────────

def pedir_importe(mensaje="  Importe (EUR): "):
    while True:
        try:
            raw = input(mensaje).strip().replace(",", ".")
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


def pedir_opcion_lista(lista, campo="opcion", permitir_texto=False):
    """Muestra una lista numerada y devuelve el indice elegido.
    Si permitir_texto=True, permite escribir directamente un valor propio."""
    for i, item in enumerate(lista, 1):
        print(f"    {i:>2}.  {item}")
    if permitir_texto:
        print(f"     0.  Escribir manualmente")
    while True:
        try:
            raw = input(f"\n  Selecciona {campo} (numero): ").strip()
            idx = int(raw) - 1
            if permitir_texto and idx == -1:
                return None  # Señal para pedir texto libre
            if 0 <= idx < len(lista):
                return idx
            error(f"Elige entre 1 y {len(lista)}.")
        except ValueError:
            error("Introduce un numero entero.")


def mostrar_lista_transacciones(lista, titulo="TRANSACCIONES"):
    """Imprime una tabla bien formateada de transacciones."""
    if not lista:
        aviso("No hay transacciones que mostrar.")
        return

    # Cabecera de tabla
    print()
    separador("-")
    col_fecha = 12
    col_tipo  = 14
    col_conc  = 18
    col_cat   = 12
    col_imp   = 10
    cab = f"  {'Fecha':<{col_fecha}} {'Tipo':<{col_tipo}} {'Concepto':<{col_conc}} {'Categoria':<{col_cat}} {'Importe':>{col_imp}}"
    print(cab)
    separador("-")

    total_ing = 0
    total_gas = 0
    for t in lista:
        tipo = t.__class__.__name__
        imp  = t.importe
        if isinstance(t, Ingreso):
            signo = "+"
            total_ing += imp
        else:
            signo = "-"
            total_gas += imp
        conc  = t.concepto[:col_conc - 1]
        cat   = t.categoria[:col_cat - 1]
        print(f"  {t.fecha:<{col_fecha}} {tipo:<{col_tipo}} {conc:<{col_conc}} {cat:<{col_cat}} {signo}{imp:>{col_imp - 1}.2f} EUR")

    separador("-")
    print(f"  {'Ingresos:':<{col_fecha + col_tipo + col_conc + col_cat}} {'+' + f'{total_ing:.2f}':>{col_imp}} EUR")
    print(f"  {'Gastos:':<{col_fecha + col_tipo + col_conc + col_cat}} {'-' + f'{total_gas:.2f}':>{col_imp}} EUR")
    separador("-")


# ─────────────────────────────────────────────────────────────
#   INICIO DE SESION
# ─────────────────────────────────────────────────────────────

def pantalla_bienvenida():
    limpiar()
    print()
    linea("=")
    fila("", "^")
    fila("G E S T O R   D E   F I N A N Z A S", "^")
    fila("", "^")
    linea("=")
    fila("Alejandro Garcia Plo  &  Alex Soler Barcelo", "^")
    separador("-")
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
        print("  Sesion guardada encontrada:")
        print()
        separador("-")
        print(f"  {'Titular':<18} {cuenta.nombre}")
        print(f"  {'Saldo':<18} {cuenta.saldo:.2f} EUR")
        print(f"  {'Transacciones':<18} {len(cuenta.transacciones)}")
        separador("-")
        print()
        opcion = input("  Cargar sesion guardada? (s/n) [ENTER=s]: ").strip().lower()
        if opcion != "n":
            ok("Sesion cargada.")
            pausar()
            return cuenta
        aviso("Se creara una cuenta nueva.")
        print()

    seccion("NUEVA CUENTA")
    print()
    nombre = pedir_texto("  Nombre del titular: ", "nombre")
    saldo  = pedir_importe("  Saldo inicial (EUR): ")
    nueva = Cuenta(nombre, saldo_inicial=saldo)
    ok(f"Cuenta '{nombre}' creada con {saldo:.2f} EUR.")
    pausar()
    return nueva


# ─────────────────────────────────────────────────────────────
#   MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("1",  "Registrar ingreso",              "MOVIMIENTOS"),
    ("2",  "Registrar gasto",                "MOVIMIENTOS"),
    ("3",  "Ver y ordenar transacciones",    "MOVIMIENTOS"),
    ("4",  "Ver saldo y balance",            "MOVIMIENTOS"),
    ("5",  "Buscar transaccion",             "MOVIMIENTOS"),
    ("6",  "Buscar por categoria",           "MOVIMIENTOS"),
    ("7",  "Buscar por rango de fechas",     "MOVIMIENTOS"),
    ("8",  "Eliminar transaccion",           "MOVIMIENTOS"),
    ("9",  "Crear presupuesto mensual",      "PRESUPUESTOS"),
    ("10", "Ver estado de presupuesto",      "PRESUPUESTOS"),
    ("11", "Comparar dos presupuestos",      "PRESUPUESTOS"),
    ("12", "Comparativa mensual historica",  "ANALISIS"),
    ("13", "Informe de anomalias",           "ANALISIS"),
    ("14", "Estadisticas graficas",          "ANALISIS"),
    ("15", "Resumen detallado + categorias", "ANALISIS"),
    ("16", "Ver historial de auditoria",     "ARCHIVOS"),
    ("17", "Exportar informe a TXT",         "ARCHIVOS"),
    ("0",  "Guardar y salir",                "SISTEMA"),
]


def mostrar_menu(cuenta):
    cabecera_pantalla("MENU PRINCIPAL", cuenta)
    grupo_actual = ""
    for codigo, etiqueta, grupo in MENU_ITEMS:
        if grupo != grupo_actual:
            grupo_actual = grupo
            pad = ANCHO - len(grupo) - 5
            print(f"  +-- {grupo} {'-' * max(1, pad)}+")
        print(f"  | {codigo:>2}.  {etiqueta:<{ANCHO - 8}}|")
    separador("-")
    print()


# ─────────────────────────────────────────────────────────────
#   ACCION: REGISTRAR TRANSACCION
# ─────────────────────────────────────────────────────────────

def accion_agregar_transaccion(cuenta, detector, tipo):
    es_ingreso = (tipo == "ingreso")
    label      = "NUEVO INGRESO" if es_ingreso else "NUEVO GASTO"
    cabecera_pantalla(label, cuenta)

    # ── Datos basicos ────────────────────────────────────────
    concepto = pedir_texto("  Concepto           : ", "concepto")
    importe  = pedir_importe("  Importe (EUR)      : ")
    fecha    = pedir_fecha("  Fecha [ENTER=hoy]  : ")

    # ── Alerta de anomalia ───────────────────────────────────
    if not es_ingreso:
        umbral = detector.calcular_umbral_dinamico(cuenta.transacciones)
        if umbral > 0 and importe > umbral:
            print()
            separador("!")
            print(f"  ! {'ATENCION - Gasto elevado':^{ANCHO - 4}} !")
            print(f"  ! Importe: {importe:.2f} EUR    Umbral habitual: {umbral:.2f} EUR{'':{ANCHO - 52}} !")
            separador("!")
            if not confirmar("Continuar con el registro de todas formas"):
                aviso("Registro cancelado.")
                pausar()
                return

    # ── Categoria con lista ──────────────────────────────────
    print()
    cats = CATEGORIAS_INGRESO if es_ingreso else CATEGORIAS_GASTO
    print("  Categoria:")
    idx_cat = pedir_opcion_lista(cats, "categoria", permitir_texto=True)
    if idx_cat is None:
        categoria = pedir_texto("  Escribe la categoria: ", "categoria")
    else:
        categoria = cats[idx_cat]

    # ── Datos especificos ────────────────────────────────────
    print()
    if es_ingreso:
        print("  Origen del ingreso:")
        origenes = ["Nomina", "Freelance", "Transferencia recibida", "Otro"]
        idx_ori = pedir_opcion_lista(origenes, "origen", permitir_texto=True)
        origen  = pedir_texto("  Escribe el origen: ", "origen") if idx_ori is None else origenes[idx_ori]

        print()
        es_fijo = input("  Es un ingreso recurrente? (s/n) [ENTER=n]: ").strip().lower() == "s"
        if es_fijo:
            print("  Frecuencia:")
            idx_f      = pedir_opcion_lista(FRECUENCIAS, "frecuencia")
            frecuencia = FRECUENCIAS[idx_f]
            t = IngresoFijo(concepto, importe, categoria, fecha, origen, frecuencia)
        else:
            t = Ingreso(concepto, importe, categoria, fecha, origen)
    else:
        print("  Metodo de pago:")
        idx_mp = pedir_opcion_lista(METODOS_PAGO, "metodo de pago", permitir_texto=True)
        metodo = pedir_texto("  Escribe el metodo: ", "metodo") if idx_mp is None else METODOS_PAGO[idx_mp]

        print()
        es_fijo = input("  Es un gasto recurrente? (s/n) [ENTER=n]: ").strip().lower() == "s"
        if es_fijo:
            print("  Frecuencia:")
            idx_f      = pedir_opcion_lista(FRECUENCIAS, "frecuencia")
            frecuencia = FRECUENCIAS[idx_f]
            t = GastoFijo(concepto, importe, categoria, fecha, metodo, frecuencia)
        else:
            t = Gasto(concepto, importe, categoria, fecha, metodo)

    # ── Resumen antes de guardar ─────────────────────────────
    print()
    separador("-")
    print(f"  {'Tipo':<16} {t.__class__.__name__}")
    print(f"  {'Concepto':<16} {t.concepto}")
    print(f"  {'Importe':<16} {t.importe:.2f} EUR")
    print(f"  {'Categoria':<16} {t.categoria}")
    print(f"  {'Fecha':<16} {t.fecha}")
    separador("-")

    try:
        cuenta.agregar_transaccion(t)
        ok(f"Registrado correctamente.  Nuevo saldo: {cuenta.saldo:.2f} EUR")
    except SaldoInsuficienteError as e:
        error(e)

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: VER Y ORDENAR TRANSACCIONES
# ─────────────────────────────────────────────────────────────

def accion_ver_transacciones(cuenta):
    cabecera_pantalla("VER TRANSACCIONES", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones registradas todavia.")
        pausar()
        return

    # Filtro por tipo
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
        lista = list(cuenta.transacciones)
        etiq  = "TODAS"

    if not lista:
        aviso("No hay transacciones para ese filtro.")
        pausar()
        return

    # Ordenacion
    print()
    print("  Ordenar por:")
    print("    1.  Fecha (mas reciente primero)")
    print("    2.  Fecha (mas antigua primero)")
    print("    3.  Importe (mayor primero)")
    print("    4.  Importe (menor primero)")
    print("    5.  Sin ordenar (orden de registro)")
    orden = input("\n  Opcion [ENTER=sin ordenar]: ").strip()

    if orden == "1":
        lista.sort(key=lambda t: t.fecha_como_datetime(), reverse=True)
    elif orden == "2":
        lista.sort(key=lambda t: t.fecha_como_datetime())
    elif orden == "3":
        lista.sort(key=lambda t: t.importe, reverse=True)
    elif orden == "4":
        lista.sort(key=lambda t: t.importe)

    print()
    print(f"  {etiq}  ({len(lista)} movimientos)")
    mostrar_lista_transacciones(lista, etiq)

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: VER SALDO
# ─────────────────────────────────────────────────────────────

def accion_ver_saldo(cuenta):
    cabecera_pantalla("SALDO Y BALANCE", cuenta)
    total_ing, total_gas, dif = cuenta.balance_ingresos_gastos()
    estado = "SUPERAVIT" if dif >= 0 else "DEFICIT"
    signo  = "+" if dif >= 0 else ""

    separador("-")
    print(f"  {'Saldo actual':<26} {cuenta.saldo:>10.2f} EUR")
    separador("-")
    print(f"  {'Total ingresos':<26} {total_ing:>10.2f} EUR")
    print(f"  {'Total gastos':<26} {total_gas:>10.2f} EUR")
    separador("-")
    print(f"  {'Balance neto  (' + estado + ')':<26} {signo}{dif:>10.2f} EUR")
    separador("-")

    # Histograma de gastos por mes
    try:
        datos = Comparador(cuenta).obtener_gastos_por_mes()
        if datos:
            seccion("GASTOS POR MES")
            max_val = max(datos.values())
            for mes, val in datos.items():
                bar_len = int((val / max_val) * 28) if max_val > 0 else 0
                barra   = "#" * bar_len
                print(f"  {mes}  |{barra:<28}|  {val:.2f} EUR")
    except Exception:
        pass

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: BUSCAR (concepto o categoria)
# ─────────────────────────────────────────────────────────────

def accion_buscar(cuenta):
    cabecera_pantalla("BUSCAR POR CONCEPTO", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones registradas.")
        pausar()
        return

    termino = pedir_texto("  Concepto a buscar: ", "termino")
    try:
        resultados = cuenta.buscar_por_concepto(termino)
        print(f"\n  {len(resultados)} resultado(s) para '{termino}':")
        mostrar_lista_transacciones(resultados)
    except TransaccionNoEncontradaError as e:
        error(e)

    pausar()


def accion_buscar_categoria(cuenta):
    cabecera_pantalla("BUSCAR POR CATEGORIA", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones registradas.")
        pausar()
        return

    # Mostrar categorias presentes en la cuenta
    cats_presentes = sorted(set(t.categoria for t in cuenta.transacciones))
    print("  Categorias registradas en tu cuenta:\n")
    idx = pedir_opcion_lista(cats_presentes, "categoria", permitir_texto=True)
    if idx is None:
        categoria = pedir_texto("  Escribe la categoria: ", "categoria")
    else:
        categoria = cats_presentes[idx]

    try:
        resultados = cuenta.buscar_por_categoria(categoria)
        total = sum(t.importe for t in resultados)
        print(f"\n  {len(resultados)} transaccion(es) en '{categoria}'  |  Total: {total:.2f} EUR")
        mostrar_lista_transacciones(resultados)
    except TransaccionNoEncontradaError as e:
        error(e)

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: BUSCAR POR RANGO DE FECHAS
# ─────────────────────────────────────────────────────────────

def accion_buscar_rango_fechas(cuenta):
    cabecera_pantalla("BUSCAR POR RANGO DE FECHAS", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones registradas.")
        pausar()
        return

    print("  Introduce el periodo a consultar.")
    print()
    fecha_ini = pedir_fecha("  Fecha inicio [ENTER=hoy]: ")
    fecha_fin = pedir_fecha("  Fecha fin    [ENTER=hoy]: ")

    try:
        resultados = cuenta.buscar_por_rango_fechas(fecha_ini, fecha_fin)
        print(f"\n  {len(resultados)} transaccion(es) entre {fecha_ini} y {fecha_fin}:")
        mostrar_lista_transacciones(resultados)
    except (TransaccionNoEncontradaError, ValueError) as e:
        error(e)

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: ELIMINAR
# ─────────────────────────────────────────────────────────────

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

    print(f"\n  {len(resultados)} coincidencia(s):")
    mostrar_lista_transacciones(resultados)

    print()
    if len(resultados) > 1:
        print("  Se eliminara la primera coincidencia.")

    if not confirmar("Confirmar eliminacion"):
        aviso("Eliminacion cancelada.")
        pausar()
        return

    try:
        eliminada = resultados[0]
        cuenta.eliminar_transaccion(eliminada.concepto)
        ok(f"'{eliminada.concepto}' eliminada.  Nuevo saldo: {cuenta.saldo:.2f} EUR")
    except (TransaccionNoEncontradaError, FinanzasError) as e:
        error(e)

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: PRESUPUESTOS
# ─────────────────────────────────────────────────────────────

def accion_crear_presupuesto(presupuestos):
    cabecera_pantalla("NUEVO PRESUPUESTO MENSUAL")

    MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    print("  Selecciona el mes:\n")
    mes_idx = pedir_opcion_lista(MESES, "mes")
    mes     = MESES[mes_idx]

    if mes in presupuestos:
        aviso(f"Ya existe un presupuesto para {mes}: {presupuestos[mes].cantidad:.2f} EUR.")
        if not confirmar("Sobreescribir"):
            aviso("Operacion cancelada.")
            pausar()
            return

    monto = pedir_importe(f"\n  Cantidad para {mes} (EUR): ")

    try:
        presupuestos[mes] = Presupuesto(mes, monto)
        ok(f"Presupuesto {mes}: {monto:.2f} EUR guardado.")
    except PresupuestoInvalidoError as e:
        error(e)

    pausar()


def accion_estado_presupuesto(cuenta, presupuestos):
    cabecera_pantalla("ESTADO DE PRESUPUESTO", cuenta)

    if not presupuestos:
        aviso("No hay presupuestos. Usa la opcion 9 para crear uno.")
        pausar()
        return

    print("  Selecciona el presupuesto:\n")
    lista_meses = list(presupuestos.keys())
    etiquetas   = [f"{m:<14} {presupuestos[m].cantidad:.2f} EUR" for m in lista_meses]
    idx = pedir_opcion_lista(etiquetas, "presupuesto")
    mes = lista_meses[idx]
    p   = presupuestos[mes]

    estado = p.estado_presupuesto(cuenta)
    pct    = min(estado["porcentaje_usado"], 100)
    bar_l  = int(pct / 4)
    barra  = "#" * bar_l + "." * (25 - bar_l)

    print()
    separador("-")
    print(f"  PRESUPUESTO  {mes.upper()}")
    separador("-")
    print(f"  {'Presupuestado':<22} {estado['presupuestado']:>10.2f} EUR")
    print(f"  {'Gastado hasta hoy':<22} {estado['gastado']:>10.2f} EUR")
    print(f"  {'Restante':<22} {estado['restante']:>10.2f} EUR")
    separador("-")
    print(f"  Uso: [{barra}] {estado['porcentaje_usado']:.1f}%")
    separador("-")

    if estado["en_superavit"]:
        ok(f"Dentro del presupuesto. Quedan {estado['restante']:.2f} EUR.")
    else:
        error(f"Presupuesto superado en {abs(estado['restante']):.2f} EUR.")

    pausar()


def accion_comparar_presupuestos(presupuestos):
    cabecera_pantalla("COMPARAR PRESUPUESTOS")

    if len(presupuestos) < 2:
        aviso("Necesitas al menos 2 presupuestos para comparar.")
        pausar()
        return

    lista_p = list(presupuestos.values())
    etiq    = [f"{p.mes:<14} {p.cantidad:.2f} EUR" for p in lista_p]

    print("  Primer presupuesto:\n")
    idx1 = pedir_opcion_lista(etiq)
    print()
    print("  Segundo presupuesto:\n")
    idx2 = pedir_opcion_lista(etiq)

    p1, p2 = lista_p[idx1], lista_p[idx2]
    dif    = abs(p1.cantidad - p2.cantidad)
    mayor  = p1 if p1.comparar(p2) else p2
    menor  = p2 if p1.comparar(p2) else p1

    print()
    separador("-")
    print(f"  COMPARATIVA DE PRESUPUESTOS")
    separador("-")
    print(f"  {p1.mes:<20} {p1.cantidad:>10.2f} EUR")
    print(f"  {p2.mes:<20} {p2.cantidad:>10.2f} EUR")
    separador("-")
    print(f"  {'Diferencia':<20} {dif:>10.2f} EUR")
    print(f"  {'Mes con mas':<20} {mayor.mes}")
    if menor.cantidad > 0:
        variacion = ((mayor.cantidad - menor.cantidad) / menor.cantidad) * 100
        print(f"  {'Variacion':<20} +{variacion:.1f}% respecto a {menor.mes}")
    separador("-")

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: ANALISIS
# ─────────────────────────────────────────────────────────────

def accion_comparativa_mensual(cuenta):
    cabecera_pantalla("COMPARATIVA MENSUAL HISTORICA", cuenta)
    Comparador(cuenta).mostrar_comparativa()
    pausar()


def accion_informe_anomalias(cuenta, detector):
    cabecera_pantalla("INFORME DE ANOMALIAS", cuenta)
    print()
    print(f"  Multiplicador  : x{detector.multiplicador}")
    print(f"  Muestra        : ultimos {detector.num_recientes} gastos")
    detector.informe_anomalias(cuenta.transacciones)
    pausar()


def accion_estadisticas(cuenta):
    """Muestra graficos de barras en consola para gastos e ingresos."""
    cabecera_pantalla("ESTADISTICAS GRAFICAS", cuenta)

    if not cuenta.transacciones:
        aviso("No hay transacciones para mostrar estadisticas.")
        pausar()
        return

    BAR_MAX = 30

    # ── Gastos por categoria ─────────────────────────────────
    gastos_cat = cuenta.obtener_gastos_por_categoria()
    if gastos_cat:
        seccion("GASTOS POR CATEGORIA")
        total_g = sum(gastos_cat.values())
        max_g   = max(gastos_cat.values())
        for cat, monto in sorted(gastos_cat.items(), key=lambda x: x[1], reverse=True):
            bar_len = int((monto / max_g) * BAR_MAX) if max_g > 0 else 0
            pct     = (monto / total_g * 100) if total_g > 0 else 0
            barra   = "#" * bar_len
            print(f"  {cat:<18} |{barra:<{BAR_MAX}}| {monto:>8.2f} EUR  {pct:>5.1f}%")
        separador("-")
        print(f"  {'TOTAL':<18}  {'':{BAR_MAX + 1}}  {total_g:>8.2f} EUR")

    # ── Ingresos por categoria ───────────────────────────────
    ing_cat = cuenta.obtener_ingresos_por_categoria()
    if ing_cat:
        seccion("INGRESOS POR CATEGORIA")
        total_i = sum(ing_cat.values())
        max_i   = max(ing_cat.values())
        for cat, monto in sorted(ing_cat.items(), key=lambda x: x[1], reverse=True):
            bar_len = int((monto / max_i) * BAR_MAX) if max_i > 0 else 0
            pct     = (monto / total_i * 100) if total_i > 0 else 0
            barra   = "#" * bar_len
            print(f"  {cat:<18} |{barra:<{BAR_MAX}}| {monto:>8.2f} EUR  {pct:>5.1f}%")
        separador("-")
        print(f"  {'TOTAL':<18}  {'':{BAR_MAX + 1}}  {total_i:>8.2f} EUR")

    # ── Evolucion mensual (gastos vs ingresos) ───────────────
    try:
        datos_g = Comparador(cuenta).obtener_gastos_por_mes()
        if datos_g:
            seccion("EVOLUCION MENSUAL DE GASTOS")
            max_v = max(datos_g.values())
            for mes, val in datos_g.items():
                bar_len = int((val / max_v) * BAR_MAX) if max_v > 0 else 0
                barra   = "#" * bar_len
                print(f"  {mes}  |{barra:<{BAR_MAX}}|  {val:.2f} EUR")
    except Exception:
        pass

    # ── Top 5 gastos ─────────────────────────────────────────
    gastos = sorted(
        [t for t in cuenta.transacciones if not isinstance(t, Ingreso)],
        key=lambda t: t.importe, reverse=True
    )[:5]
    if gastos:
        seccion("TOP 5 GASTOS")
        for i, t in enumerate(gastos, 1):
            print(f"  {i}.  {t.concepto:<22} {t.importe:>8.2f} EUR  ({t.fecha})")

    pausar()


def accion_resumen_detallado(cuenta):
    cabecera_pantalla("RESUMEN DETALLADO", cuenta)
    cuenta.generar_resumen()
    cuenta.mostrar_reporte_categorias()
    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: HISTORIAL DE AUDITORIA
# ─────────────────────────────────────────────────────────────

def accion_historial_auditoria():
    cabecera_pantalla("HISTORIAL DE AUDITORIA")

    ruta = "auditoria.log"
    if not os.path.exists(ruta):
        aviso("No existe ningun registro de auditoria todavia.")
        pausar()
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.readlines()
    except IOError as e:
        error(f"No se pudo leer el archivo: {e}")
        pausar()
        return

    if not lineas:
        aviso("El registro de auditoria esta vacio.")
        pausar()
        return

    # Opciones de visualizacion
    print("  El registro tiene " + str(len(lineas)) + " entradas.")
    print()
    print("  Mostrar:")
    print("    1.  Ultimas 20 entradas")
    print("    2.  Ultimas 50 entradas")
    print("    3.  Todo el historial")
    opcion = input("\n  Opcion [ENTER=ultimas 20]: ").strip()

    if opcion == "2":
        mostrar = lineas[-50:]
    elif opcion == "3":
        mostrar = lineas
    else:
        mostrar = lineas[-20:]

    print()
    separador("-")
    for linea_log in mostrar:
        print(f"  {linea_log.rstrip()}")
    separador("-")
    print(f"\n  Mostrando {len(mostrar)} de {len(lineas)} entradas.")

    pausar()


# ─────────────────────────────────────────────────────────────
#   ACCION: EXPORTAR
# ─────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────
#   ACCION: GUARDAR Y SALIR
# ─────────────────────────────────────────────────────────────

def accion_guardar_salir(cuenta):
    cabecera_pantalla("GUARDAR Y SALIR", cuenta)
    print()
    separador("-")
    print(f"  {'Titular':<20} {cuenta.nombre}")
    print(f"  {'Saldo':<20} {cuenta.saldo:.2f} EUR")
    print(f"  {'Transacciones':<20} {len(cuenta.transacciones)}")
    separador("-")
    print()

    if confirmar("Guardar y salir"):
        try:
            GestorArchivos.guardar_datos(cuenta)
            GestorArchivos.guardar_backup_binario(cuenta)
            print()
            linea("=")
            fila("  Datos guardados correctamente.", "<")
            fila("  Hasta pronto!", "<")
            linea("=")
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
        "6":  lambda: accion_buscar_categoria(cuenta),
        "7":  lambda: accion_buscar_rango_fechas(cuenta),
        "8":  lambda: accion_eliminar(cuenta),
        "9":  lambda: accion_crear_presupuesto(presupuestos),
        "10": lambda: accion_estado_presupuesto(cuenta, presupuestos),
        "11": lambda: accion_comparar_presupuestos(presupuestos),
        "12": lambda: accion_comparativa_mensual(cuenta),
        "13": lambda: accion_informe_anomalias(cuenta, detector),
        "14": lambda: accion_estadisticas(cuenta),
        "15": lambda: accion_resumen_detallado(cuenta),
        "16": lambda: accion_historial_auditoria(),
        "17": lambda: accion_exportar_txt(cuenta),
    }

    while True:
        mostrar_menu(cuenta)
        opcion = input("  Opcion: ").strip()

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
            error(f"Opcion no valida. Elige entre 0 y {max(int(k) for k in ACCIONES)}.")
            pausar()


if __name__ == "__main__":
    main()
