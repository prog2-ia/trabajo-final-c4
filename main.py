from Presupuesto import Presupuesto
from Gasto import Gasto
from Ingreso import Ingreso
from Cuenta import Cuenta
if __name__ == '__main__':
    print("--- TRANSACCIONES ---")
    nomina = Ingreso("Nómina Febrero", 1500, "Salario", "27/02/2026", "Empresa S.A.")
    compra = Gasto("Mercadona", 80, "Comida", "28/02/2026", "Tarjeta de Débito")

    print(nomina.mostrar())
    print(compra.mostrar())

    print("\n--- PRESUPUESTOS ---")
    p1 = Presupuesto("Alquiler", 800)
    p2 = Presupuesto("Comida", 300)

    total = p1.sumar(p2)
    comparar = p1.comparar(p2)

    print(f"Suma total: {total}€")
    print(f"¿El alquiler es mayor que la comida?: {comparar}")
print("\n--- CUENTA ---")
cuenta1 = Cuenta("Cuenta Principal")

cuenta1.agregar_transaccion(nomina)
cuenta1.agregar_transaccion(compra)

cuenta1.mostrar()