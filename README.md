[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/09uckVan)

# Gestor de Finanzas Personales por Alejandro García Plo y Alex Soler Barceló.

##  Propósito del Proyecto

Este proyecto es una aplicación de consola desarrollada en Python que permite a los usuarios llevar un control detallado de sus finanzas personales.

##  Características Principales

-Gestión de Cuentas: Registro del saldo inicial y actualización automática con cada transacción.
-Control de Transacciones: Permite añadir Ingresos (con su origen) y Gastos (con su método de pago).
-Detección de Anomalías: Incorpora un algoritmo inteligente que avisa al usuario si intenta registrar un gasto inusualmente alto en comparación con su media histórica.
-Presupuestos: Creación de presupuestos mensuales y capacidad para compararlos entre sí.
-Análisis Mensual: Genera una comparativa automática de los gastos mes a mes, indicando si han incrementado o reducido.

## Estructura del Proyecto

El código está diseñado separando en distintas clases:
* `main.py`: Punto de entrada de la aplicación y gestión del menú interactivo.
* `Cuenta.py`: Manejo del saldo y el historial de transacciones.
* `Transaccion.py`, `Gasto.py`, `Ingreso.py`: Implementación de herencia y polimorfismo para los movimientos financieros.
* `Presupuesto.py`: Creación y comparación de metas financieras.
* `Comparar.py` y `DetectarAnomalia.py`: Lógica de análisis de datos y alertas.

