"""
Excepciones personalizadas para el Gestor de Finanzas.
Permite identificar con precisión cada tipo de error del dominio.
"""


class FinanzasError(Exception):
    """Excepción base del proyecto. Todas las demás heredan de esta."""
    pass


# ── Errores de validación de datos ──────────────────────────────────────────

class ImporteInvalidoError(FinanzasError):
    """Se lanza cuando el importe no es un número positivo."""
    def __init__(self, valor=None):
        msg = (
            f"El importe '{valor}' no es válido. Debe ser un número mayor que 0."
            if valor is not None
            else "El importe debe ser un número mayor que 0."
        )
        super().__init__(msg)


class FechaInvalidaError(FinanzasError):
    """Se lanza cuando la fecha no respeta el formato DD/MM/YYYY."""
    def __init__(self, valor=None):
        msg = (
            f"La fecha '{valor}' no tiene el formato correcto (DD/MM/YYYY)."
            if valor is not None
            else "Formato de fecha incorrecto. Usa DD/MM/YYYY."
        )
        super().__init__(msg)


class ConceptoVacioError(FinanzasError):
    """Se lanza cuando el concepto de una transacción está vacío."""
    def __init__(self):
        super().__init__("El concepto de la transacción no puede estar vacío.")


class CategoriaVaciaError(FinanzasError):
    """Se lanza cuando la categoría está vacía."""
    def __init__(self):
        super().__init__("La categoría no puede estar vacía.")


# ── Errores de cuenta ────────────────────────────────────────────────────────

class SaldoInsuficienteError(FinanzasError):
    """Se lanza cuando un gasto dejaría el saldo en negativo (si se activa la restricción)."""
    def __init__(self, saldo_actual, importe):
        super().__init__(
            f"Saldo insuficiente: intentas gastar {importe:.2f}€ "
            f"pero solo tienes {saldo_actual:.2f}€."
        )


class TransaccionNoEncontradaError(FinanzasError):
    """Se lanza al buscar o eliminar una transacción que no existe."""
    def __init__(self, concepto=None):
        msg = (
            f"No se encontró ninguna transacción con el concepto '{concepto}'."
            if concepto
            else "La transacción indicada no existe en la cuenta."
        )
        super().__init__(msg)


class CuentaNoInicializadaError(FinanzasError):
    """Se lanza cuando se intenta operar sobre una cuenta que no se ha creado."""
    def __init__(self):
        super().__init__("La cuenta no ha sido inicializada correctamente.")


# ── Errores de presupuesto ───────────────────────────────────────────────────

class PresupuestoInvalidoError(FinanzasError):
    """Se lanza cuando el monto del presupuesto no es válido."""
    def __init__(self, valor=None):
        msg = (
            f"El presupuesto '{valor}' no es válido. Debe ser un número mayor que 0."
            if valor is not None
            else "El presupuesto debe ser un número mayor que 0."
        )
        super().__init__(msg)


class PresupuestoDuplicadoError(FinanzasError):
    """Se lanza cuando se intenta crear un presupuesto para un mes ya existente."""
    def __init__(self, mes):
        super().__init__(f"Ya existe un presupuesto para el mes '{mes}'.")


# ── Errores de archivo ───────────────────────────────────────────────────────

class ArchivoCorruptoError(FinanzasError):
    """Se lanza cuando el archivo CSV tiene un formato irreconocible."""
    def __init__(self, ruta):
        super().__init__(f"El archivo '{ruta}' está dañado o tiene un formato incorrecto.")


class ArchivoNoEncontradoError(FinanzasError):
    """Se lanza cuando no se encuentra el archivo de datos."""
    def __init__(self, ruta):
        super().__init__(f"No se encontró el archivo de datos en '{ruta}'.")
