from abc import ABC, abstractmethod
from datetime import datetime
from Excepciones import ImporteInvalidoError, FechaInvalidaError, ConceptoVacioError, CategoriaVaciaError


class Transaccion(ABC):
    FORMATO_FECHA = "%d/%m/%Y"

    def __init__(self, concepto, importe, categoria, fecha):
        # El orden importa: los setters validan, asignamos en orden lógico
        self.concepto = concepto
        self.importe = importe
        self.categoria = categoria
        self.fecha = fecha

    # ── Importe ──────────────────────────────────────────────────────────────

    @property
    def importe(self):
        return self.__importe

    @importe.setter
    def importe(self, valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ImporteInvalidoError(valor)
        if valor <= 0:
            raise ImporteInvalidoError(valor)
        self.__importe = valor

    # ── Concepto ─────────────────────────────────────────────────────────────

    @property
    def concepto(self):
        return self.__concepto

    @concepto.setter
    def concepto(self, valor):
        if not valor or not str(valor).strip():
            raise ConceptoVacioError()
        self.__concepto = str(valor).strip()

    # ── Categoría ────────────────────────────────────────────────────────────

    @property
    def categoria(self):
        return self.__categoria

    @categoria.setter
    def categoria(self, valor):
        if not valor or not str(valor).strip():
            raise CategoriaVaciaError()
        self.__categoria = str(valor).strip()

    # ── Fecha ────────────────────────────────────────────────────────────────

    @property
    def fecha(self):
        return self.__fecha

    @fecha.setter
    def fecha(self, valor):
        if not valor or not str(valor).strip():
            raise FechaInvalidaError(valor)
        try:
            datetime.strptime(str(valor).strip(), self.FORMATO_FECHA)
        except ValueError:
            raise FechaInvalidaError(valor)
        self.__fecha = str(valor).strip()

    # ── Utilidades ───────────────────────────────────────────────────────────

    def fecha_como_datetime(self):
        """Devuelve la fecha como objeto datetime para comparaciones."""
        return datetime.strptime(self.__fecha, self.FORMATO_FECHA)

    @abstractmethod
    def mostrar(self):
        return f'[{self.fecha}] {self.concepto}: {self.importe:.2f}€ | Categoría: {self.categoria}'

    def __repr__(self):
        return f"{self.__class__.__name__}(concepto='{self.concepto}', importe={self.importe}, fecha='{self.fecha}')"
