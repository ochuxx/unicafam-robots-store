# FrontEnd/pages/05_ventas.py
from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import clientes_mock, empleados_mock, inventario_mock, robots_mock, ventas_mock, detalle_ventas_mock
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────
# Claves reales de los mocks relevantes:
#   clientes_mock:  "nit", "nombre"
#   empleados_mock: "id" (int), "nombre"
#   robots_mock:    "id" (str "SER-XXX"), "nombre"
#   inventario_mock: "id" (código barras), "precio", "id_robot"
#   ventas_mock:    "id", "fecha_venta", "total", "id_cliente" (NIT), "id_empleado" (int)
#   detalle_ventas_mock: "id", "id_venta", "id_inventario", "cantidad", "subtotal"
# ──────────────────────────────────────────────────────────────────────

# Índices para búsqueda rápida
_CLIENTES_POR_NIT = {c["nit"]: c for c in clientes_mock}
_EMPLEADOS_POR_ID = {e["id"]:  e for e in empleados_mock}

# Opciones para selects del formulario (todos los registros con búsqueda)
OPCIONES_CLIENTE  = [f"{c['nit']} - {c['nombre']}"  for c in clientes_mock]
OPCIONES_EMPLEADO = [f"{e['id']} - {e['nombre']}"   for e in empleados_mock]

# Catálogo de robots con precio desde inventario, incluyendo id_inventario
_CATALOGO_ROBOTS = []
_vistos = set()
for inv in inventario_mock:
    rid = inv["id_robot"]
    if rid not in _vistos:
        robot = next((r for r in robots_mock if r["id"] == rid), None)
        if robot:
            _CATALOGO_ROBOTS.append({
                "id_robot":      robot["id"],          # str: "SER-001"
                "nombre":        robot["nombre"],
                "precio":        inv["precio"],
                "id_inventario": inv["id"],            # código de barras
            })
            _vistos.add(rid)

OPCIONES_ROBOT = [f"{r['id_robot']} - {r['nombre']} (${r['precio']:,.0f})" for r in _CATALOGO_ROBOTS]
_ROBOTS_POR_OPCION = {
    f"{r['id_robot']} - {r['nombre']} (${r['precio']:,.0f})": r
    for r in _CATALOGO_ROBOTS
}

# ──────────────────────────────────────────────────────────────────────
# Helpers de visualización para la tabla
# ──────────────────────────────────────────────────────────────────────

def _nombre_cliente(nit: str) -> str:
    c = _CLIENTES_POR_NIT.get(nit)
    return f"{nit} - {c['nombre']}" if c else nit

def _nombre_empleado(id_emp) -> str:
    e = _EMPLEADOS_POR_ID.get(id_emp)
    return f"{id_emp} - {e['nombre']}" if e else str(id_emp)

def _construir_filas() -> list:
    return [
        {
            "id":          v["id"],
            "fecha_venta": v["fecha_venta"],
            "cliente":     _nombre_cliente(v["id_cliente"]),
            "empleado":    _nombre_empleado(v["id_empleado"]),
            "total":       f"${v['total']:,.0f}",
            "_id_cliente": v["id_cliente"],
            "_id_empleado": v["id_empleado"],
        }
        for v in ventas_mock
    ]

# ──────────────────────────────────────────────────────────────────────
# Estado del formulario de detalles
# ──────────────────────────────────────────────────────────────────────

_contador_detalle  = 0
_filas_detalle: dict = {}


def _generar_id_venta() -> int:
    """Calcula el próximo ID basado en el máximo ID actual en ventas_mock."""
    if not ventas_mock:
        return 1
    return max(v["id"] for v in ventas_mock) + 1


def _generar_id_detalle_persistente() -> int:
    """Calcula el próximo ID para detalle_ventas_mock."""
    if not detalle_ventas_mock:
        return 1
    return max(d["id"] for d in detalle_ventas_mock) + 1


def _generar_id_detalle_temporal() -> int:
    global _contador_detalle
    _contador_detalle += 1
    return _contador_detalle

# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────

def page(content_container):
    with content_container:
        ui.label("Gestión de Ventas").classes("page-title")
        ui.label("Registro de transacciones con detalles").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        # ── Cabecera de la venta ─────────────────────────────────────
        ui.label("Datos de la venta").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 8px;"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="8px", gap="16px", columns=2, max_width="100%",
        )
        form.build()

        form.fecha    = form.add_field("date",   "Fecha de venta",
                                       value=datetime.now().strftime("%Y-%m-%d"))
        form.cliente  = form.add_field("select", "Cliente",              options=OPCIONES_CLIENTE)
        form.cliente.props("use-input input-debounce=300 fill-input hide-selected")

        form.empleado = form.add_field("select", "Empleado responsable", options=OPCIONES_EMPLEADO)
        form.empleado.props("use-input input-debounce=300 fill-input hide-selected")

        # ── Detalle de productos ─────────────────────────────────────
        ui.separator().classes("my-4")
        ui.label("Productos vendidos").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 8px;"
        )

        detalles_container  = ui.column().classes("w-full gap-2")
        total_general_label = ui.label("Total general: $0").classes("text-h6 text-right").style(
            "color: var(--teal-light); margin-top: 16px;"
        )

        # ── Funciones de detalle ─────────────────────────────────────

        def _actualizar_total():
            total = sum(
                (d["cantidad"].value or 0) * d["precio"]
                for d in _filas_detalle.values()
            )
            total_general_label.set_text(f"Total general: ${total:,.0f}")

        def _actualizar_subtotal(idx: int):
            data = _filas_detalle.get(idx)
            if data:
                subtotal = (data["cantidad"].value or 0) * data["precio"]
                data["subtotal"].set_text(f"${subtotal:,.0f}")
                _actualizar_total()

        def _eliminar_fila(fila_element, idx: int):
            fila_element.clear()
            _filas_detalle.pop(idx, None)
            _actualizar_total()

        def _actualizar_precio(idx: int):
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
            nuevo_id = _generar_id_detalle_temporal()
            with detalles_container:
                with ui.row().classes("w-full gap-2 items-center").style(
                    "margin-bottom: 8px;"
                ) as fila:
                    robot_sel = ui.select(
                        options=OPCIONES_ROBOT,
                        label="Robot",
                        value=OPCIONES_ROBOT[0] if OPCIONES_ROBOT else None,
                        on_change=lambda _i=nuevo_id: _actualizar_precio(_i),
                    ).classes("flex-1")
                    robot_sel.props("use-input input-debounce=300 fill-input hide-selected")

                    cantidad_inp = ui.number(
                        value=1, min=1, label="Cantidad",
                        on_change=lambda _i=nuevo_id: _actualizar_subtotal(_i),
                    ).classes("w-24")

                    subtotal_lbl = ui.label("$0").classes("w-24 text-right")

                    ui.button("🗑️", on_click=lambda _f=fila, _i=nuevo_id: _eliminar_fila(_f, _i)) \
                      .props("flat").style("color: var(--text-muted);")

                    # Inicializar con el primer robot si existe
                    precio_inicial = 0
                    id_inventario_inicial = None
                    if OPCIONES_ROBOT:
                        primera_opcion = OPCIONES_ROBOT[0]
                        robot_info = _ROBOTS_POR_OPCION.get(primera_opcion)
                        if robot_info:
                            precio_inicial = robot_info["precio"]
                            id_inventario_inicial = robot_info["id_inventario"]

                    _filas_detalle[nuevo_id] = {
                        "fila":          fila,
                        "robot":         robot_sel,
                        "cantidad":      cantidad_inp,
                        "subtotal":      subtotal_lbl,
                        "precio":        precio_inicial,
                        "id_inventario": id_inventario_inicial,
                    }
                    _actualizar_precio(nuevo_id)
            _actualizar_total()

        def _guardar_venta():
            if not form.cliente.value or not form.empleado.value:
                ui.notify("Debe seleccionar cliente y empleado", type="negative")
                return
            if not _filas_detalle:
                ui.notify("Debe agregar al menos un producto", type="negative")
                return

            total_venta = sum(
                (d["cantidad"].value or 0) * d["precio"]
                for d in _filas_detalle.values()
            )
            nuevo_id_venta = _generar_id_venta()

            # Persistir cabecera en ventas_mock
            nit_cliente = form.cliente.value.split(" - ")[0].strip()
            id_empleado = int(form.empleado.value.split(" - ")[0].strip())
            ventas_mock.append({
                "id":          nuevo_id_venta,
                "fecha_venta": form.fecha.value,
                "total":       total_venta,
                "id_cliente":  nit_cliente,
                "id_empleado": id_empleado,
            })

            # Persistir detalles en detalle_ventas_mock
            for det in _filas_detalle.values():
                id_inventario = det["id_inventario"]
                cantidad = det["cantidad"].value
                subtotal = cantidad * det["precio"]
                nuevo_id_detalle = _generar_id_detalle_persistente()
                detalle_ventas_mock.append({
                    "id":           nuevo_id_detalle,
                    "id_venta":     nuevo_id_venta,
                    "id_inventario": id_inventario,
                    "cantidad":     cantidad,
                    "subtotal":     subtotal,
                })

            ui.notify(
                f"✅ Venta #{nuevo_id_venta} registrada — {len(_filas_detalle)} producto(s) — "
                f"Total: ${total_venta:,.0f}",
                type="positive", position="top",
            )

            # Limpiar formulario y detalles temporales
            form.fecha.value    = datetime.now().strftime("%Y-%m-%d")
            form.cliente.value  = None
            form.empleado.value = None
            for data in list(_filas_detalle.values()):
                data["fila"].clear()
            _filas_detalle.clear()
            tabla_ventas.set_data(_construir_filas())
            _actualizar_total()

        # ── Botones de acción del detalle ────────────────────────────
        with ui.row().classes("justify-end mt-2"):
            ui.button("➕ Agregar producto", on_click=_agregar_fila) \
              .props("flat").style("border: 1px solid var(--teal-mid);")

        with ui.row().classes("justify-end mt-4"):
            ui.button("Registrar venta", on_click=_guardar_venta) \
              .props("unelevated").style("background: var(--teal-mid); color: white;")

        # ── Tabla de ventas ──────────────────────────────────────────
        ui.separator().classes("my-6")
        ui.label("Listado de ventas").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 12px;"
        )

        columnas_ventas = [
            {"label": "ID",          "field": "id",          "width": "60px",  "filter_mode": "exact"},
            {"label": "Fecha",       "field": "fecha_venta", "width": "160px", "filter_mode": "startswith"},
            {"label": "Cliente",     "field": "cliente",     "width": "220px", "filter_mode": "contains"},
            {"label": "Empleado",    "field": "empleado",    "width": "200px", "filter_mode": "contains"},
            {"label": "Total",       "field": "total",       "width": "120px", "filter_mode": "contains", "align": "right"},
        ]

        tabla_ventas = SmartTable(
            columns=columnas_ventas,
            data=_construir_filas(),
            rows_per_page=10,
            show_pagination=True,
            show_actions=False,      # Las ventas no se editan ni eliminan
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla_ventas.build()