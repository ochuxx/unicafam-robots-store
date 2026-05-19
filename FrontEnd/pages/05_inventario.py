from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import robots_mock, proveedores_mock, inventario_mock
from datetime import datetime
import re

# ──────────────────────────────────────────────────────────────────────
# Funciones auxiliares y validaciones
# ──────────────────────────────────────────────────────────────────────
_ROBOTS_POR_ID = {r["id"]: r for r in robots_mock}
_PROVS_POR_NIT = {p["nit"]: p for p in proveedores_mock}

OPCIONES_ROBOT = [f"{r['id']} - {r['nombre']}" for r in robots_mock]
OPCIONES_PROV = [f"{p['nit']} - {p['nombre_empresa']}" for p in proveedores_mock]

def solo_digitos_codigo(valor):
    if not valor:
        return True
    if not re.match(r'^\d+$', valor):
        return "El código de barras solo puede contener números"
    return True

def validar_seleccion_robot(valor):
    if not valor:
        return True
    if valor not in OPCIONES_ROBOT:
        return "Seleccione un robot válido de la lista"
    return True

def validar_seleccion_proveedor(valor):
    if not valor:
        return True
    if valor not in OPCIONES_PROV:
        return "Seleccione un proveedor válido de la lista"
    return True

def _nombre_robot(id_robot: str) -> str:
    r = _ROBOTS_POR_ID.get(id_robot)
    return r["nombre"] if r else id_robot

def _nombre_proveedor(nit: str) -> str:
    p = _PROVS_POR_NIT.get(nit)
    return p["nombre_empresa"] if p else nit

def _construir_filas() -> list:
    return [
        {
            "codigo": item["id"],
            "robot_nombre": _nombre_robot(item["id_robot"]),
            "proveedor_nombre": _nombre_proveedor(item["id_proveedor"]),
            "precio": f"{item['precio']:,.0f}".replace(",", "."),
            "stock": item["stock"],
            "fecha_ingreso": item["fecha_registro"],
            "_id_robot": item["id_robot"],
            "_id_proveedor": item["id_proveedor"],
        }
        for item in inventario_mock
    ]

def _registrar_en_backend(datos: dict) -> dict:
    nuevo = {
        "id": datos["codigo"],
        "id_robot": datos["id_robot"],
        "id_proveedor": datos["id_proveedor"],
        "precio": datos["precio"],
        "stock": datos["stock"],
        "fecha_registro": datos["fecha_registro"],
    }
    inventario_mock.append(nuevo)
    return nuevo

def _actualizar_en_backend(codigo: str, datos: dict) -> bool:
    for item in inventario_mock:
        if item["id"] == codigo:
            item.update(datos)
            return True
    return False

def _eliminar_en_backend(codigo: str) -> bool:
    global inventario_mock
    longitud_anterior = len(inventario_mock)
    inventario_mock[:] = [i for i in inventario_mock if i["id"] != codigo]
    return len(inventario_mock) < longitud_anterior

# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────
def page(content_container):
    with content_container:
        ui.label("Gestión de Inventario").classes("page-title")
        ui.label("Registro de existencias de robots").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        ui.label("Registrar entrada de inventario").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar(form, tabla_inventario),
            submit_text="Registrar inventario",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        # Código de barras
        form.codigo = form.add_field(
            "input", "Código de barras",
            placeholder="7501234567890",
            required=True,
            max_length=20,
            validation=solo_digitos_codigo
        )
        form.codigo.props('inputmode=numeric')

        # Robot (con validación de selección)
        form.robot = form.add_field(
            "select", "Robot",
            options=OPCIONES_ROBOT,
            required=True,
            validation=validar_seleccion_robot
        )
        form.robot.props("use-input input-debounce=300 fill-input hide-selected")
        form.robot.props('input-maxlength=50')   # limitador de texto en búsqueda

        # Proveedor (con validación de selección)
        form.proveedor = form.add_field(
            "select", "Proveedor",
            options=OPCIONES_PROV,
            required=True,
            validation=validar_seleccion_proveedor
        )
        form.proveedor.props("use-input input-debounce=300 fill-input hide-selected")
        form.proveedor.props('input-maxlength=50')

        # Precio
        form.precio = form.add_field(
            "number", "Precio de venta (COP)",
            placeholder="0",
            value=0,
            required=True,
            validation={'min': 1}
        )

        # Stock (entero)
        form.stock = form.add_field(
            "number", "Cantidad en stock",
            placeholder="0",
            value=0,
            required=True,
            integer_only=True,
            validation={'min': 1}
        )

        # Fecha
        form.fecha = form.add_field(
            "date", "Fecha de ingreso",
            value=datetime.now().strftime("%Y-%m-%d"),
            required=True
        )

        ui.separator().classes("my-6")

        ui.label("Listado de inventario").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        columnas_inventario = [
            {"label": "Código de barras", "field": "codigo", "width": "160px", "filter_mode": "exact"},
            {"label": "Robot", "field": "robot_nombre", "width": "200px", "filter_mode": "contains"},
            {"label": "Proveedor", "field": "proveedor_nombre", "width": "200px", "filter_mode": "contains"},
            {"label": "Precio (COP)", "field": "precio", "width": "130px", "filter_mode": "exact", "align": "right"},
            {"label": "Stock", "field": "stock", "width": "90px", "filter_mode": "exact", "align": "right"},
            {"label": "Fecha ingreso", "field": "fecha_ingreso", "width": "140px", "filter_mode": "startswith"},
        ]

        acciones = {
            "editar": {"icon": "edit", "color": "amber", "tooltip": "Editar inventario"},
            "eliminar": {"icon": "delete", "color": "red", "tooltip": "Eliminar item"},
        }

        tabla_inventario = SmartTable(
            columns=columnas_inventario,
            data=_construir_filas(),
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion(accion, fila, tabla_inventario),
            row_key="codigo",
            max_height="500px",
            filterable=True,
        )
        tabla_inventario.build()

# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────
def _registrar(f: SmartForm, tabla_ref: SmartTable) -> None:
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    id_robot = f.robot.value.split(" - ")[0].strip()
    nit_proveedor = f.proveedor.value.split(" - ")[0].strip()
    codigo = f.codigo.value.strip()

    if any(i["id"] == codigo for i in inventario_mock):
        ui.notify(f"Ya existe un item con código {codigo}", type="warning")
        return

    nuevo = _registrar_en_backend({
        "codigo": codigo,
        "id_robot": id_robot,
        "id_proveedor": nit_proveedor,
        "precio": f.precio.value,
        "stock": int(f.stock.value),
        "fecha_registro": f.fecha.value,
    })

    ui.notify(
        f"✅ Inventario registrado: {_nombre_robot(nuevo['id_robot'])} — Stock: {nuevo['stock']}",
        type="positive",
    )

    f.codigo.value = ""
    f.robot.value = None
    f.proveedor.value = None
    f.precio.value = 0
    f.stock.value = 0
    f.fecha.value = datetime.now().strftime("%Y-%m-%d")
    f.clear_errors()

    tabla_ref.set_data(_construir_filas())

def _manejar_accion(accion: str, fila: dict, tabla_ref: SmartTable) -> None:
    if accion == "editar":
        _dialogo_edicion(fila, tabla_ref)
    elif accion == "eliminar":
        _dialogo_eliminar(fila, tabla_ref)

def _dialogo_edicion(fila: dict, tabla_ref: SmartTable) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar inventario — {fila['codigo']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 8px;"
        )
        ui.label(f"Robot: {fila['robot_nombre']}").classes("text-caption")
        ui.label(f"Fecha ingreso: {fila['fecha_ingreso']}").classes("text-caption mb-4")

        precio_actual = int(fila["precio"].replace(".", "")) if isinstance(fila["precio"], str) else fila["precio"]
        inp_precio = ui.number("Precio (COP)", value=precio_actual, min=1, step=1000).classes("w-full")
        inp_stock = ui.number("Stock", value=fila["stock"], min=0, step=1).classes("w-full")

        nit_actual = fila.get("_id_proveedor", "")
        prov_actual = next(
            (f"{p['nit']} - {p['nombre_empresa']}" for p in proveedores_mock if p["nit"] == nit_actual),
            None,
        )
        inp_proveedor = ui.select(
            options=OPCIONES_PROV,
            label="Proveedor",
            value=prov_actual,
        ).classes("w-full")
        inp_proveedor.props("use-input input-debounce=300 fill-input hide-selected")
        inp_proveedor.props('input-maxlength=50')

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def guardar():
                if not inp_precio.value or inp_precio.value <= 0:
                    ui.notify("El precio debe ser mayor a cero", type="negative")
                    return
                if inp_stock.value is None or inp_stock.value < 0:
                    ui.notify("El stock no puede ser negativo", type="negative")
                    return
                if not inp_proveedor.value:
                    ui.notify("Selecciona un proveedor", type="negative")
                    return
                if inp_proveedor.value not in OPCIONES_PROV:
                    ui.notify("Seleccione un proveedor válido de la lista", type="negative")
                    return

                nit_nuevo = inp_proveedor.value.split(" - ")[0].strip()
                ok = _actualizar_en_backend(fila["codigo"], {
                    "precio": inp_precio.value,
                    "stock": int(inp_stock.value),
                    "id_proveedor": nit_nuevo,
                })
                if ok:
                    ui.notify(f"✅ Inventario {fila['codigo']} actualizado", type="positive")
                    tabla_ref.set_data(_construir_filas())
                    dialogo.close()
                else:
                    ui.notify("No se encontró el item para actualizar", type="negative")

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()

def _dialogo_eliminar(fila: dict, tabla_ref: SmartTable) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar item de inventario").classes("text-h6").style(
            "color: #F44336; margin-bottom: 8px;"
        )
        ui.label(
            f"¿Deseas eliminar el código {fila['codigo']} "
            f"({fila['robot_nombre']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")
            def confirmar():
                ok = _eliminar_en_backend(fila["codigo"])
                if ok:
                    ui.notify(f"🗑️ Item {fila['codigo']} eliminado", type="positive")
                    tabla_ref.set_data(_construir_filas())
                    dialogo.close()
                else:
                    ui.notify("No se encontró el item para eliminar", type="negative")
            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")
    dialogo.open()