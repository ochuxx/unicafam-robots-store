# FrontEnd/pages/06_ventas.py
"""
Módulo de gestión de ventas.

Proporciona una interfaz para registrar nuevas ventas con múltiples productos
(detalles) y visualizar el listado de ventas existentes, incluyendo un diálogo
con los productos vendidos en cada transacción.

Relaciones clave:
- Una venta (tabla 'ventas_mock') tiene un ID único (id).
- Cada detalle (tabla 'detalle_ventas_mock') pertenece a una venta mediante
  el campo 'id_venta' (clave foránea).
- Al guardar una venta, se genera primero el ID de la venta y luego se asignan
  los detalles con ese mismo ID.
"""

from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import (
    clientes_mock,
    empleados_mock,
    inventario_mock,
    robots_mock,
    ventas_mock,
    detalle_ventas_mock,
)
from datetime import datetime

# ----------------------------------------------------------------------
# Datos auxiliares (mapeos, opciones, catálogos)
# ----------------------------------------------------------------------
_CLIENTES_POR_NIT = {c["nit"]: c for c in clientes_mock}
_EMPLEADOS_POR_ID = {e["id"]: e for e in empleados_mock}
_INVENTARIO_POR_ID = {i["id"]: i for i in inventario_mock}
_ROBOTS_POR_ID = {r["id"]: r for r in robots_mock}

OPCIONES_CLIENTE = [f"{c['nit']} - {c['nombre']}" for c in clientes_mock]
OPCIONES_EMPLEADO = [f"{e['id']} - {e['nombre']}" for e in empleados_mock]

# Catálogo de robots únicos (basado en el inventario)
_CATALOGO_ROBOTS = []
_vistos = set()
for inv in inventario_mock:
    rid = inv["id_robot"]
    if rid not in _vistos:
        robot = _ROBOTS_POR_ID.get(rid)
        if robot:
            _CATALOGO_ROBOTS.append({
                "id_robot": robot["id"],
                "nombre": robot["nombre"],
                "precio": inv["precio"],
                "id_inventario": inv["id"],
            })
            _vistos.add(rid)

OPCIONES_ROBOT = [
    f"{r['id_robot']} - {r['nombre']} (${r['precio']:,.0f})".replace(",", ".")
    for r in _CATALOGO_ROBOTS
]
_ROBOTS_POR_OPCION = {opc: r for opc, r in zip(OPCIONES_ROBOT, _CATALOGO_ROBOTS)}


# ----------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------
def _nombre_cliente(nit: str) -> str:
    """Devuelve la representación 'NIT - Nombre' para un cliente dado su NIT."""
    c = _CLIENTES_POR_NIT.get(nit)
    return f"{nit} - {c['nombre']}" if c else nit


def _nombre_empleado(id_emp) -> str:
    """Devuelve la representación 'ID - Nombre' para un empleado dado su ID."""
    e = _EMPLEADOS_POR_ID.get(id_emp)
    return f"{id_emp} - {e['nombre']}" if e else str(id_emp)


def _construir_filas() -> list:
    """Construye la lista de filas para la tabla de ventas, en el formato
    esperado por SmartTable."""
    return [
        {
            "id": v["id"],
            "fecha_venta": v["fecha_venta"],
            "cliente": _nombre_cliente(v["id_cliente"]),
            "empleado": _nombre_empleado(v["id_empleado"]),
            "total": f"${v['total']:,.0f}".replace(",", "."),
            "_id_cliente": v["id_cliente"],
            "_id_empleado": v["id_empleado"],
        }
        for v in ventas_mock
    ]


# Variables globales para el manejo de los detalles temporales de la venta
_contador_detalle = 0          # Contador para IDs TEMPORALES (solo durante la creación)
_filas_detalle: dict = {}      # Almacena los elementos UI y datos de cada producto temporal


def _generar_id_venta() -> int:
    """Genera un nuevo ID secuencial para una venta (persistente en ventas_mock)."""
    return max((v["id"] for v in ventas_mock), default=0) + 1


def _generar_id_detalle_persistente() -> int:
    """Genera un nuevo ID secuencial para un detalle de venta (persistente en detalle_ventas_mock)."""
    return max((d["id"] for d in detalle_ventas_mock), default=0) + 1


def _generar_id_detalle_temporal() -> int:
    """Genera un ID TEMPORAL (no persistente) para un producto durante la creación
    de la venta. Se reinicia a 0 después de guardar la venta."""
    global _contador_detalle
    _contador_detalle += 1
    return _contador_detalle


def _dialogo_detalles_venta(fila: dict):
    """Muestra un diálogo con los detalles (productos) de una venta existente.
    Filtra los detalles por 'id_venta' para mostrar solo los pertenecientes a la venta."""
    venta_id = fila["id"]
    venta = next((v for v in ventas_mock if v["id"] == venta_id), None)
    if not venta:
        ui.notify("Venta no encontrada", type="error")
        return

    # Relación: obtener todos los detalles cuya id_venta coincida con el ID de la venta
    detalles = [d for d in detalle_ventas_mock if d["id_venta"] == venta_id]
    cliente_nombre = fila["cliente"]
    empleado_nombre = fila["empleado"]

    with ui.dialog() as dialog, ui.card().style(
        "min-width: 650px; max-width: 900px; padding: 20px;"
    ):
        ui.label(f"Detalles de la venta #{venta_id}").classes("text-h5 text-primary")
        ui.label(f"Registrada el {venta['fecha_venta']}").classes(
            "text-caption"
        ).style("margin-bottom: 20px;")

        with ui.grid(columns=2).classes("gap-4").style("margin-bottom: 24px;"):
            ui.label("Cliente:").classes("text-weight-bold")
            ui.label(cliente_nombre)
            ui.label("Empleado responsable:").classes("text-weight-bold")
            ui.label(empleado_nombre)
            ui.label("Total:").classes("text-weight-bold")
            ui.label(fila["total"]).classes("text-h6 text-primary")

        ui.separator()
        ui.label("Productos vendidos").classes(
            "text-subtitle1 text-weight-bold"
        ).style("margin: 16px 0 12px 0;")

        if detalles:
            productos = []
            for det in detalles:
                inv = _INVENTARIO_POR_ID.get(det["id_inventario"])
                if inv:
                    robot = _ROBOTS_POR_ID.get(inv["id_robot"])
                    nombre_robot = robot["nombre"] if robot else "Desconocido"
                    productos.append({
                        "producto": nombre_robot,
                        "cantidad": det["cantidad"],
                        "precio_unitario": f"${inv['precio']:,.0f}".replace(",", "."),
                        "subtotal": f"${det['subtotal']:,.0f}".replace(",", "."),
                    })
            columns = [
                {"name": "producto", "label": "Producto", "field": "producto"},
                {"name": "cantidad", "label": "Cantidad", "field": "cantidad", "align": "right"},
                {"name": "precio", "label": "Precio unit.", "field": "precio_unitario", "align": "right"},
                {"name": "subtotal", "label": "Subtotal", "field": "subtotal", "align": "right"},
            ]
            pagination = {"rowsPerPage": 5} if len(productos) > 5 else None
            ui.table(columns=columns, rows=productos, row_key="producto", pagination=pagination).classes("w-full")
        else:
            ui.label("No hay productos registrados para esta venta.").style("color: gray; margin: 8px 0;")

        with ui.row().classes("justify-end mt-4"):
            ui.button("Cerrar", on_click=dialog.close).props("flat")
    dialog.open()


# ----------------------------------------------------------------------
# Función principal de la página
# ----------------------------------------------------------------------
def page(content_container):
    """Construye la página de ventas dentro del contenedor proporcionado."""
    with content_container:
        ui.label("Gestión de Ventas").classes("page-title")
        ui.label("Registro de transacciones con detalles").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        # --- Formulario de datos de la venta ---
        ui.label("Datos de la venta").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 8px;"
        )
        form = SmartForm(title="", subtitle="", padding="8px", gap="16px", columns=2, max_width="100%")
        form.build()
        form.fecha = form.add_field("date", "Fecha de venta", value=datetime.now().strftime("%Y-%m-%d"))
        form.cliente = form.add_field("select", "Cliente", options=OPCIONES_CLIENTE)
        form.cliente.props("use-input input-debounce=300 fill-input hide-selected")
        form.empleado = form.add_field("select", "Empleado responsable", options=OPCIONES_EMPLEADO)
        form.empleado.props("use-input input-debounce=300 fill-input hide-selected")

        ui.separator().classes("my-4")

        # --- Lista dinámica de productos ---
        ui.label("Productos vendidos").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 8px;"
        )
        detalles_container = ui.column().classes("w-full gap-2")
        total_general_label = ui.label("Total general: $0").classes("text-h6 text-right").style(
            "color: var(--teal-light); margin-top: 16px;"
        )

        def _actualizar_total():
            """Recalcula el total general a partir de los productos actuales
            y actualiza el label correspondiente."""
            total = sum(
                (d["cantidad"].value or 0) * d["precio"]
                for d in _filas_detalle.values()
            )
            total_general_label.set_text(f"Total general: ${total:,.0f}".replace(",", "."))

        def _actualizar_subtotal(idx: int):
            """Actualiza el subtotal de una fila específica (por su ID temporal)
            y luego refresca el total general."""
            data = _filas_detalle.get(idx)
            if data:
                subtotal = (data["cantidad"].value or 0) * data["precio"]
                data["subtotal"].set_text(f"${subtotal:,.0f}".replace(",", "."))
                _actualizar_total()

        def _eliminar_fila(fila_element, idx: int):
            """Elimina visualmente una fila de producto y la remueve del
            diccionario de detalles."""
            fila_element.clear()
            _filas_detalle.pop(idx, None)
            _actualizar_total()

        def _actualizar_precio(idx: int):
            """Cuando se cambia el robot seleccionado, actualiza el precio
            unitario y el ID de inventario asociado."""
            data = _filas_detalle.get(idx)
            if not data:
                return
            seleccion = data["robot"].value
            robot_info = _ROBOTS_POR_OPCION.get(seleccion)
            if robot_info:
                data["precio"] = robot_info["precio"]
                data["id_inventario"] = robot_info["id_inventario"]
            else:
                data["precio"] = 0
                data["id_inventario"] = None
            _actualizar_subtotal(idx)

        def _agregar_fila():
            """Agrega una nueva fila (producto) al formulario de venta."""
            nuevo_id = _generar_id_detalle_temporal()
            with detalles_container:
                with ui.row().classes("w-full gap-2 items-center").style("margin-bottom: 8px;") as fila:
                    robot_sel = ui.select(
                        options=OPCIONES_ROBOT,
                        label="Robot",
                        value=OPCIONES_ROBOT[0] if OPCIONES_ROBOT else None,
                        on_change=lambda _i=nuevo_id: _actualizar_precio(_i),
                    ).classes("flex-1")
                    robot_sel.props("use-input input-debounce=300 fill-input hide-selected")
                    cantidad_inp = ui.number(
                        value=1,
                        min=1,
                        label="Cantidad",
                        on_change=lambda _i=nuevo_id: _actualizar_subtotal(_i),
                    ).classes("w-24")
                    subtotal_lbl = ui.label("$0").classes("w-24 text-right")
                    ui.button("🗑️", on_click=lambda _f=fila, _i=nuevo_id: _eliminar_fila(_f, _i)).props("flat").style("color: var(--text-muted);")

                    # Precio e inventario inicial (primer robot de la lista)
                    precio_inicial = 0
                    id_inventario_inicial = None
                    if OPCIONES_ROBOT:
                        robot_info = _ROBOTS_POR_OPCION.get(OPCIONES_ROBOT[0])
                        if robot_info:
                            precio_inicial = robot_info["precio"]
                            id_inventario_inicial = robot_info["id_inventario"]

                    _filas_detalle[nuevo_id] = {
                        "fila": fila,
                        "robot": robot_sel,
                        "cantidad": cantidad_inp,
                        "subtotal": subtotal_lbl,
                        "precio": precio_inicial,
                        "id_inventario": id_inventario_inicial,
                    }
                    _actualizar_precio(nuevo_id)
            _actualizar_total()

        # --- Botón para agregar producto ---
        with ui.row().classes("justify-end mt-2"):
            ui.button("➕ Agregar producto", on_click=_agregar_fila).props("flat").style(
                "border: 1px solid var(--teal-mid);"
            )

        # --- Botón Registrar venta (con la corrección principal y relación explícita) ---
        def _guardar_venta():
            """Valida los datos, crea la venta y sus detalles en la base de datos mock,
            estableciendo la relación venta-detalle mediante 'id_venta' en cada detalle.
            Luego limpia el formulario y refresca la interfaz, reiniciando el total a $0."""
            global _contador_detalle

            # Validaciones
            if not form.cliente.value or not form.empleado.value:
                ui.notify("Debe seleccionar cliente y empleado", type="negative")
                return
            if not _filas_detalle:
                ui.notify("Debe agregar al menos un producto", type="negative")
                return

            # Cálculo del total de la venta
            total_venta = sum(
                (d["cantidad"].value or 0) * d["precio"]
                for d in _filas_detalle.values()
            )

            # 1. Crear la venta (obtener su ID)
            nuevo_id_venta = _generar_id_venta()
            nit_cliente = form.cliente.value.split(" - ")[0].strip()
            id_empleado = int(form.empleado.value.split(" - ")[0].strip())
            ventas_mock.append({
                "id": nuevo_id_venta,
                "fecha_venta": form.fecha.value,
                "total": total_venta,
                "id_cliente": nit_cliente,
                "id_empleado": id_empleado,
            })

            # 2. Crear los detalles vinculados a la venta mediante 'id_venta'
            for det in _filas_detalle.values():
                id_inventario = det["id_inventario"]
                cantidad = det["cantidad"].value
                subtotal = cantidad * det["precio"]
                nuevo_id_detalle = _generar_id_detalle_persistente()
                detalle_ventas_mock.append({
                    "id": nuevo_id_detalle,
                    "id_venta": nuevo_id_venta,     # ← Clave foránea que relaciona con ventas_mock
                    "id_inventario": id_inventario,
                    "cantidad": cantidad,
                    "subtotal": subtotal,
                })

            ui.notify(
                f"Venta #{nuevo_id_venta} registrada — {len(_filas_detalle)} producto(s) — Total: ${total_venta:,.0f}".replace(",", "."),
                type="positive",
                position="top",
            )

            # Reiniciar el formulario
            form.fecha.value = datetime.now().strftime("%Y-%m-%d")
            form.cliente.value = None
            form.empleado.value = None

            # Limpiar todas las filas de productos (visual y datos)
            for data in list(_filas_detalle.values()):
                data["fila"].clear()
            _filas_detalle.clear()

            # Reiniciar el contador de IDs temporales
            _contador_detalle = 0

            # Actualizar la tabla de ventas
            tabla_ventas.set_data(_construir_filas())

            # Forzar la actualización del total general (mostrar $0)
            total_general_label.set_text("Total general: $0")
            _actualizar_total()      # redundante pero seguro
            ui.update()              # garantiza el refresco de la UI

        with ui.row().classes("justify-end mt-4"):
            ui.button("Registrar venta", on_click=_guardar_venta).props("unelevated").style(
                "background: var(--teal-mid); color: white;"
            )

        # --- Tabla de ventas existentes ---
        ui.separator().classes("my-6")
        ui.label("Listado de ventas").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 12px;"
        )

        columnas_ventas = [
            {"label": "ID", "field": "id", "width": "60px", "filter_mode": "exact"},
            {"label": "Fecha", "field": "fecha_venta", "width": "160px", "filter_mode": "startswith"},
            {"label": "Cliente", "field": "cliente", "width": "220px", "filter_mode": "contains"},
            {"label": "Empleado", "field": "empleado", "width": "200px", "filter_mode": "contains"},
            {"label": "Total", "field": "total", "width": "120px", "filter_mode": "contains", "align": "right"},
        ]
        acciones = {"detalles": {"icon": "visibility", "color": "teal", "tooltip": "Ver detalles de la venta"}}
        tabla_ventas = SmartTable(
            columns=columnas_ventas,
            data=_construir_filas(),
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _dialogo_detalles_venta(fila) if accion == "detalles" else None,
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla_ventas.build()