# 🚀 SmartBot Solutions - Sistema de Gestión para Venta y Soporte de Robots

![Estado](https://img.shields.io/badge/Estado-Producción-brightgreen)  
![Frontend](https://img.shields.io/badge/Frontend-NiceGUI-blue)  
![Datos](https://img.shields.io/badge/Datos-Mock-orange)

## 📌 Introducción

**SmartBot Solutions** es una empresa tecnológica dedicada a la venta, distribución y soporte técnico de robots inteligentes para hogares, empresas e instituciones educativas.

Con el crecimiento de la empresa, se ha implementado un **sistema de gestión completo** que permite administrar clientes, inventario, ventas y soporte técnico de manera eficiente mediante una interfaz web moderna construida con **NiceGUI** y una base de datos relacional simulada (mock) para demostrar su funcionalidad.

## ❗ Planteamiento del Problema

El sistema resuelve los siguientes problemas identificados inicialmente:

- Duplicidad de registros → **Validación de NIT/ID en formularios**.
- Errores en el control de stock → **Actualización automática en inventario**.
- Dificultad para consultar información histórica → **Tablas con filtros y paginación**.
- Desorganización de clientes y proveedores → **CRUD completo con búsqueda**.
- Falta de trazabilidad en soporte técnico → **Registro y cambio de estado de tickets**.

## 🎯 Objetivos

### Objetivo General
Implementar una aplicación web funcional que gestione clientes, inventario, ventas y soporte técnico de forma organizada, eficiente y escalable.

### Objetivos Específicos
- ✅ Diseñar componentes reutilizables (SmartForm, SmartTable) con NiceGUI.
- ✅ Establecer relaciones entre entidades mediante claves foráneas en los datos mock.
- ✅ Crear formularios dinámicos con validación y diseño responsive.
- ✅ Controlar el inventario de robots (stock, precios, proveedores).
- ✅ Registrar ventas con múltiples productos y cálculo automático de totales.
- ✅ Gestionar soporte técnico con estados y fechas de actualización.
- ✅ Facilitar consultas y reportes administrativos (analítica de ventas y soporte).

## 📐 Alcance del Proyecto

El sistema permite (vía interfaz web):

- Registro, edición y eliminación de **clientes** (con NIT único).
- Registro, edición y eliminación de **robots** (número de serie único).
- Administración de **proveedores** (NIT, contacto, teléfono, correo).
- Gestión de **empleados** (documento, nombre, cargo, contacto).
- Control de **inventario** (código de barras, precio, stock, robot, proveedor).
- Registro de **ventas** con selección de cliente, empleado y múltiples robots (detalle dinámico).
- Seguimiento de **soporte técnico** (tickets con estado y fecha de última actualización).
- **Analítica** integrada: robots más vendidos, clientes con mayor facturación, estado del soporte.
- **Monitoreo en vivo** con actualización automática cada 3 segundos.

## ⚙️ Requerimientos del Sistema

### Requerimientos Funcionales
- ✅ Registrar nuevos clientes.
- ✅ Registrar robots en inventario.
- ✅ Actualizar el stock de productos (desde inventario).
- ✅ Registrar ventas (con múltiples productos).
- ✅ Relacionar clientes con compras realizadas.
- ✅ Registrar proveedores.
- ✅ Registrar empleados.
- ✅ Registrar solicitudes de soporte técnico.
- ✅ Consultar historial de ventas (tabla con filtros).
- ✅ Consultar robots con bajo stock (en monitoreo).

### Requerimientos No Funcionales
- ✅ Fácil de usar (interfaz intuitiva, sidebar colapsable, tema oscuro).
- ✅ Organizado y estructurado (código modular con componentes reutilizables).
- ✅ Escalable (fácil de conectar a una base de datos real en el futuro).
- ✅ Rápido en consultas básicas (filtrado y ordenamiento en cliente).
- ✅ Capaz de evitar duplicidad de información (validación en backend mock).

## 🗃️ Estructura de Datos (Mock)

Se generan **1000 registros por tabla** con relaciones coherentes. Las entidades principales son:

1. **Clientes** (NIT, nombre, correo, teléfono, dirección, fecha_registro)
2. **Proveedores** (NIT, nombre_empresa, contacto, teléfono, correo)
3. **Robots** (id_serie, nombre, descripción, tipo)
4. **Empleados** (id, nombre, cargo, correo, teléfono)
5. **Inventario** (código_barras, precio, stock, fecha_registro, id_proveedor, id_robot)
6. **Ventas** (id, fecha_venta, total, id_cliente, id_empleado)
7. **Detalle_Venta** (id, id_venta, id_inventario, cantidad, subtotal)
8. **Soporte_Técnico** (id, fecha_reporte, fecha_actualizacion, problema, estado, id_cliente, id_robot)

## 🔗 Relaciones Entre Tablas 

- Un **cliente** puede tener muchas **ventas** (1:N).
- Un **empleado** puede registrar muchas **ventas** (1:N).
- Un **proveedor** puede suministrar muchos **robots** (a través de inventario, 1:N).
- Una **venta** puede contener varios **robots** (N:M a través de Detalle_Venta).
- Un **robot** puede aparecer en múltiples **ventas** (N:M a través de Detalle_Venta).
- Un **cliente** puede generar múltiples **solicitudes de soporte** (1:N).
- Un **robot** puede tener varios **registros de soporte técnico** (1:N).

## 🖥️ Tecnologías Utilizadas

- **Python 3.10+**
- **NiceGUI** – Framework para interfaz web reactiva.
- **Pandas** – Procesamiento de datos para analítica.
- **CSS personalizado** – Estilos oscuros temáticos (teal/dark).
- **JavaScript** – Toggle del sidebar y manejo de slots de tabla.
- **Arquitectura modular**:
  - `components/forms.py` – SmartForm (formularios con grid).
  - `components/table.py` – SmartTable (tablas con filtros, paginación, acciones).
  - `config/global_styles.py` – Estilos globales y sidebar.
  - `pages/` – Cada sección es un módulo independiente.
  - `mock_data.py` – Generador de datos ficticios.

## 📝 Formularios del Sistema (interfaz)

### Clientes
- NIT, nombre, correo, teléfono, dirección, fecha de registro.

### Robots
- Número de serie, nombre, descripción, tipo.

### Proveedores
- NIT, nombre empresa, persona de contacto, teléfono, correo.

### Empleados
- Documento de identidad, nombre completo, cargo, correo, teléfono.

### Inventario
- Código de barras, robot (select), proveedor (select), precio, stock, fecha de ingreso.

### Ventas
- Fecha de venta, cliente (select), empleado responsable.
- Lista dinámica de productos (robot + cantidad) con cálculo de subtotal y total general.

### Soporte Técnico
- Fecha del reporte, cliente (select), robot (select), problema reportado.

## 📊 Reportes y Analítica

- **Monitoreo en vivo**: tarjetas con ventas totales, clientes, stock, soportes abiertos + tabla de últimas ventas + bajo stock + soporte reciente (actualización cada 3s).
- **Analítica**: robots más vendidos (con barra de participación), clientes con mayor facturación, estado del soporte técnico (tarjetas de conteo).

## 🚀 Instalación y Ejecución

1. Clonar el repositorio.
2. Instalar dependencias:
   ```bash
   pip install nicegui pandas
3. Ejecutar la aplicación:
   ```bash
   python main.py
4. Abrir navegador en http://localhost:8080