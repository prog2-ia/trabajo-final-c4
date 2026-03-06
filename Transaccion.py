class Transaccion:
    def __init__(self, concepto, importe, categoria, fecha):
        if importe <= 0:
            print("Importe invalido")
            return
        self.concepto = concepto
        self.importe = importe
        self.categoria = categoria
        self.fecha = fecha

    def mostrar(self):
        return f'[{self.fecha}] {self.concepto}: {self.importe}'