# Auditoria.py
from datetime import datetime


class Auditable:
    """
    Clase Mixin diseñada para añadir capacidades de registro (logging)
    a cualquier otra clase mediante herencia (TEMA 06 y TEMA 10).
    """

    def registrar_auditoria(self, accion):
        """
        Escribe un registro en un archivo de texto con la fecha y hora exactas.
        """
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linea_registro = f"[{fecha_hora}] AUDITORÍA: {accion}\n"

        try:
            # Abrimos el archivo en modo 'a' (append) para añadir al final (Tema 10)
            with open("auditoria.log", "a", encoding="utf-8") as archivo:
                archivo.write(linea_registro)
        except IOError as e:
            # Si hay un error con el archivo, al menos lo mostramos por consola
            print(f"Error interno: No se pudo escribir en el registro de auditoría ({e})")