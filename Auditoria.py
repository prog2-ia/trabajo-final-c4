# Auditoria.py
from datetime import datetime


class Auditable:
    """

    """

    def registrar_auditoria(self, accion):
        """
        Escribe un registro en un archivo de texto con la fecha y hora exactas.
        """
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linea_registro = f"[{fecha_hora}] AUDITORÍA: {accion}\n"

        try:
            with open("auditoria.log", "a", encoding="utf-8") as archivo:
                archivo.write(linea_registro)
        except IOError as e:
            # Si hay un error con el archivo, al menos lo mostramos por consola
            print(f"Error interno: No se pudo escribir en el registro de auditoría ({e})")