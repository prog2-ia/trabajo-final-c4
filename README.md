[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/09uckVan)

# Gestor de Finanzas Personales — Alejandro García Plo & Alex Soler Barceló

## Propósito del Proyecto

Aplicación de consola desarrollada en Python (v5.0) para llevar un control detallado de las finanzas personales. Permite registrar ingresos y gastos, gestionar presupuestos mensuales, detectar anomalías de gasto, analizar tendencias y exportar informes, todo con persistencia automática de datos entre sesiones.

## Características Principales

- **Gestión de cuenta**: Registro del saldo inicial y actualización automática con cada transacción. Soporta restricción de saldo negativo configurable.
- **Transacciones**: Añadir, eliminar y buscar ingresos y gastos (puntuales o fijos/recurrentes). Búsqueda por concepto, categoría o rango de fechas.
- **Tipos de transacción**: Ingreso, IngresoFijo, Gasto y GastoFijo, con soporte de frecuencias (Mensual, Semanal, Anual) y métodos de pago.
- **Presupuestos mensuales**: Creación de presupuestos por mes, consulta del estado (gastado vs. presupuestado) y comparación entre dos presupuestos.
- **Detección de anomalías**: Algoritmo configurable que avisa cuando un gasto supera un umbral dinámico calculado a partir de la media de los N gastos anteriores multiplicada por un factor.
- **Comparativa mensual**: Análisis de la evolución de gastos mes a mes con variación porcentual, mes de mayor y menor gasto.
- **Estadísticas gráficas**: Gráficos de barras en consola para gastos e ingresos por categoría, evolución mensual de gastos y top 5 gastos.
- **Auditoría**: Registro automático de todas las operaciones relevantes (creación de cuenta, adición y eliminación de transacciones) en `auditoria.log` con fecha y hora exactas. Visualizable desde el propio menú.
- **Persistencia de datos**: Guardado y carga automática en CSV (`datos.csv`), copia de seguridad binaria (`backups/seguridad.dat`) y presupuestos en JSON (`presupuestos.json`).
- **Exportación**: Generación de informes completos en texto plano (`.txt`) con resumen, desglose por categoría e historial de transacciones.

## Estructura del Proyecto

| Archivo | Descripción |
|---|---|
| `main.py` | Punto de entrada, menú interactivo y toda la lógica de pantalla (v5.0) |
| `Cuenta.py` | Gestión del saldo, historial de transacciones y estadísticas; hereda de `Auditable` |
| `Transaccion.py` | Clase base abstracta con validación de importe, fecha, concepto y categoría |
| `Ingreso.py` | Transacción de ingreso puntual (con origen) |
| `IngresoFijo.py` | Ingreso recurrente con frecuencia configurable |
| `Gasto.py` | Transacción de gasto puntual (con método de pago) |
| `GastoFijo.py` | Gasto recurrente con frecuencia configurable |
| `Presupuesto.py` | Creación, comparación y seguimiento de presupuestos mensuales |
| `Comparar.py` | Análisis y comparativa de gastos mes a mes con variación porcentual |
| `DetectarAnomalia.py` | Detector de gastos anómalos mediante umbral dinámico configurable |
| `Auditoria.py` | Mixin `Auditable` que escribe entradas en `auditoria.log` |
| `GestorArchivos.py` | Persistencia en CSV, JSON y backup binario (pickle); exportación a TXT |
| `Excepciones.py` | Jerarquía de excepciones personalizadas del dominio |

## Archivos Generados en Ejecución

| Archivo | Contenido |
|---|---|
| `datos.csv` | Cuenta y transacciones (guardado principal) |
| `presupuestos.json` | Presupuestos mensuales activos |
| `backups/seguridad.dat` | Copia de seguridad binaria completa de la cuenta |
| `auditoria.log` | Registro de operaciones con fecha y hora |
| `informe.txt` | Informe exportado manualmente desde el menú |

## Menú Principal (opciones disponibles)

1. Añadir ingreso
2. Añadir gasto
3. Ver transacciones
4. Ver saldo
5. Buscar por concepto
6. Buscar por categoría
7. Buscar por rango de fechas
8. Eliminar transacción
9. Crear presupuesto
10. Estado del presupuesto
11. Comparar presupuestos
12. Comparativa mensual de gastos
13. Informe de anomalías
14. Estadísticas gráficas
15. Resumen detallado
16. Historial de auditoría
17. Exportar informe a TXT
0. Guardar y salir

## Ejecución

```bash
python main.py
```

Requiere Python 3.8 o superior. No depende de librerías externas.
