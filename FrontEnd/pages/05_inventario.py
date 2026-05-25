from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from components.loading import LoadingOverlay, with_spinner
from mock_data import robots_mock, proveedores_mock, inventario_mock
from datetime import datetime
import re
from dotenv import load_dotenv
import os
import requests
import json
import asyncio

load_dotenv()
GAS_URL = os.getenv("GAS_URL", "").strip()

# ──────────────────────────────────────────────────────────────────────
# Funciones auxiliares y validaciones
# ──────────────────────────────────────────────────────────────────────
_ROBOTS_POR_ID: dict = {}
_PROVS_POR_NIT: dict = {}

OPCIONES_ROBOT: list = []
OPCIONES_PROV: list = []

def _reconstruir_catalogos():
    _ROBOTS_POR_ID.clear()
    _ROBOTS_POR_ID.update({r["id"]: r for r in robots_mock})
    _PROVS_POR_NIT.clear()
    _PROVS_POR_NIT.update({p["nit"]: p for p in proveedores_mock})
    OPCIONES_ROBOT[:] = [f"{r['id']} - {r['nombre']}" for r in robots_mock]
    OPCIONES_PROV[:] = [f"{p['nit']} - {p['nombre_empresa']}" for p in proveedores_mock]

def _catalogos_desde_mock():
    _reconstruir_catalogos()

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
            "id_inventario": item["id"],
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

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (conexión a Google Apps Script)
# ──────────────────────────────────────────────────────────────────────
def registrar_inventario_en_backend(datos: dict) -> dict:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {
        "action": "set_inventarios",
        "precio": datos["precio"],
        "stock": datos["stock"],
        "id_robot": datos["id_robot"],
        "id_proveedor": datos["id_proveedor"],
    }
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al registrar inventario"))
    return data

def actualizar_inventario_en_backend(id_inventario: str, datos: dict) -> dict:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "edit_inventarios", "id_inventario": id_inventario}
    payload.update(datos)
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al actualizar inventario"))
    return data

def eliminar_inventario_en_backend(id_inventario: str) -> dict:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "delete_inventarios", "id_inventario": id_inventario}
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al eliminar inventario"))
    return data

def obtener_inventarios_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_inventarios", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener inventarios"))
    return data.get("data", [])

def _obtener_robots_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_robots", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener robots"))
    global robots_mock
    data_list = data.get("data", [])
    if data_list:
        robots_mock[:] = data_list
    return data_list

def _obtener_proveedores_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_proveedores", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener proveedores"))
    global proveedores_mock
    data_list = data.get("data", [])
    if data_list:
        proveedores_mock[:] = data_list
    return data_list

async def _recargar_inventario_async(tabla_ref: SmartTable) -> None:
    if GAS_URL:
        try:
            await asyncio.to_thread(_obtener_robots_desde_backend)
            await asyncio.to_thread(_obtener_proveedores_desde_backend)
            inventarios = await asyncio.to_thread(obtener_inventarios_desde_backend)
            if inventarios:
                inventario_mock[:] = inventarios
        except Exception:
            ui.notify("No se pudo sincronizar con Apps Script; usando datos locales", type="warning")
    _reconstruir_catalogos()
    tabla_ref.set_data(_construir_filas())

# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────
def page(content_container):
    with content_container:
        _loading = LoadingOverlay()
        _loading.build()

        if GAS_URL:
            async def _cargar():
                _loading.show()
                await asyncio.sleep(0.05)
                try:
                    await asyncio.to_thread(_obtener_robots_desde_backend)
                    await asyncio.to_thread(_obtener_proveedores_desde_backend)
                    inventarios = await asyncio.to_thread(obtener_inventarios_desde_backend)
                    if inventarios:
                        inventario_mock[:] = inventarios
                except Exception:
                    ui.notify("No se pudieron cargar datos desde Apps Script", type="warning")
                finally:
                    _reconstruir_catalogos()
                    form.robot.options = list(OPCIONES_ROBOT)
                    form.proveedor.options = list(OPCIONES_PROV)
                    form.robot.update()
                    form.proveedor.update()
                    tabla_inventario.set_data(_construir_filas())
                    _loading.hide()
            ui.timer(0.1, lambda: asyncio.ensure_future(_cargar()), once=True)
        else:
            _catalogos_desde_mock()

        ui.label("Gestión de Inventario").classes("page-title")
        ui.label("Registro de existencias de robots").classes("page-subtitle").style("margin-bottom: 24px;")

        ui.label("Registrar entrada de inventario").classes("text-h6").style("color: var(--teal-light);")

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar(form, tabla_inventario, _loading),
            submit_text="Registrar inventario",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        form.robot = form.add_field(
            "select", "Robot",
            options=OPCIONES_ROBOT,
            required=True,
            validation=validar_seleccion_robot
        )
        form.robot.props("use-input input-debounce=300 fill-input hide-selected")
        form.robot.props('input-maxlength=50')

        form.proveedor = form.add_field(
            "select", "Proveedor",
            options=OPCIONES_PROV,
            required=True,
            validation=validar_seleccion_proveedor
        )
        form.proveedor.props("use-input input-debounce=300 fill-input hide-selected")
        form.proveedor.props('input-maxlength=50')

        form.precio = form.add_field(
            "number", "Precio de venta (COP)",
            placeholder="0",
            value=0,
            required=True,
            validation={'min': 1}
        )

        form.stock = form.add_field(
            "number", "Cantidad en stock",
            placeholder="0",
            value=0,
            required=True,
            integer_only=True,
            validation={'min': 1}
        )

        ui.separator().classes("my-6")

        ui.label("Listado de inventario").classes("text-h6").style("color: var(--teal-light);")

        columnas_inventario = [
            {"label": "ID Inventario", "field": "id_inventario", "width": "160px", "filter_mode": "exact"},
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
            on_action=lambda accion, fila: _manejar_accion(accion, fila, tabla_inventario, _loading),
            row_key="id_inventario",
            max_height="500px",
            filterable=True,
        )
        tabla_inventario.build()

# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────
async def _registrar(f: SmartForm, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    id_robot = f.robot.value.split(" - ")[0].strip()
    nit_proveedor = f.proveedor.value.split(" - ")[0].strip()

    async def hacer():
        if GAS_URL:
            result = await asyncio.to_thread(
                registrar_inventario_en_backend,
                {
                    "precio": f.precio.value,
                    "stock": int(f.stock.value),
                    "id_robot": id_robot,
                    "id_proveedor": nit_proveedor,
                }
            )
            nuevo_id = str(result.get("id", ""))
        else:
            nuevo_id = f.id_inventario.value.strip()
            inventario_mock.append({
                "id": nuevo_id,
                "id_robot": id_robot,
                "id_proveedor": nit_proveedor,
                "precio": f.precio.value,
                "stock": int(f.stock.value),
                "fecha_registro": f.fecha.value,
            })
        ui.notify(
            f"✅ Inventario registrado: {_nombre_robot(id_robot)} — Stock: {int(f.stock.value)}",
            type="positive",
        )
        f.id_inventario.value = ""
        f.robot.value = None
        f.proveedor.value = None
        f.precio.value = 0
        f.stock.value = 0
        f.fecha.value = datetime.now().strftime("%Y-%m-%d")
        f.clear_errors()
        return nuevo_id

    async def refrescar():
        if GAS_URL:
            await _recargar_inventario_async(tabla_ref)
        else:
            tabla_ref.set_data(_construir_filas())

    await with_spinner(_loading, hacer, refresh=refrescar, loading_after_action=True)

def _manejar_accion(accion: str, fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if accion == "editar":
        _dialogo_edicion(fila, tabla_ref, _loading)
    elif accion == "eliminar":
        _dialogo_eliminar(fila, tabla_ref, _loading)

def _dialogo_edicion(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar inventario — {fila['id_inventario']}").classes("text-h6").style(
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

            async def guardar():
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

                async def editar():
                    if GAS_URL:
                        await asyncio.to_thread(
                            actualizar_inventario_en_backend,
                            fila["id_inventario"],
                            {
                                "precio": inp_precio.value,
                                "stock": int(inp_stock.value),
                                "id_proveedor": nit_nuevo,
                                "id_robot": fila.get("_id_robot", ""),
                            }
                        )
                    else:
                        inventario_item = next((i for i in inventario_mock if i["id"] == fila["id_inventario"]), None)
                        if inventario_item:
                            inventario_item["precio"] = inp_precio.value
                            inventario_item["stock"] = int(inp_stock.value)
                            inventario_item["id_proveedor"] = nit_nuevo
                            inventario_item["id_robot"] = fila.get("_id_robot", "")
                    ui.notify(f"✅ Inventario {fila['id_inventario']} actualizado", type="positive")
                    dialogo.close()

                async def refrescar():
                    if GAS_URL:
                        await _recargar_inventario_async(tabla_ref)
                    else:
                        tabla_ref.set_data(_construir_filas())

                await with_spinner(_loading, editar, refresh=refrescar, loading_after_action=True)

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()

def _dialogo_eliminar(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar item de inventario").classes("text-h6").style("color: #F44336; margin-bottom: 8px;")
        ui.label(
            f"¿Deseas eliminar el ID {fila['id_inventario']} "
            f"({fila['robot_nombre']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def confirmar():
                async def eliminar():
                    if GAS_URL:
                        await asyncio.to_thread(eliminar_inventario_en_backend, fila["id_inventario"])
                    else:
                        inventario_mock[:] = [i for i in inventario_mock if i["id"] != fila["id_inventario"]]
                    ui.notify(f"🗑️ Item {fila['id_inventario']} eliminado", type="positive")
                    dialogo.close()

                async def refrescar():
                    if GAS_URL:
                        await _recargar_inventario_async(tabla_ref)
                    else:
                        tabla_ref.set_data(_construir_filas())

                await with_spinner(_loading, eliminar, refresh=refrescar, loading_after_action=True)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")
    dialogo.open()
