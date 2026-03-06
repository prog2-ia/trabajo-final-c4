from Ingreso import Ingreso
class Cuenta:
    def __init__(self, nombre):
        self.nombre = nombre
        self.transacciones = []
        self.saldo = 0

    def agregar_transaccion(self, transaccion):
        self.transacciones.append(transaccion)

        if type(transaccion) == Ingreso:
            self.saldo = self.saldo + transaccion.importe
        else:
            self.saldo = self.saldo - transaccion.importe

    def mostrar(self):
        print(f"\nCuenta: {self.nombre}")
        print("Movimientos:")
        for t in self.transacciones:
            print(t.mostrar())
        print(f"Saldo actual: {self.saldo}€")