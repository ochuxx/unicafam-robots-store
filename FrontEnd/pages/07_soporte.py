from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import clientes_mock, robots_mock, soporte_mock
from datetime import datetime
import re
from components.loading import LoadingOverlay, with_spinner
from dotenv import load_dotenv
import os
import requests
import json
import asyncio

load_dotenv()
GAS_URL = os.getenv("GAS_URL", "").strip()

ESTADOS_TICKET = ["Abierto", "En progreso", "Resuelto", "Cerrado"]
OPCIONES_CLIENTE: list = []
OPCIONES_ROBOT: list = []

def _reconstruir_catalogos():
    OPCIONES_CLIENTE[:] = [f"{c['nit']} - {c['nombre']}" for c in clientes_mock]
    OPCIONES_ROBOT[:] = [f"{r['id']} - {r['nombre']}" for r in robots_mock]

def _catalogos_desde_mock():
    _reconstruir_catalogos()

# ----------------------------------------------------------------------
# Funciones de validación personalizada
# ----------------------------------------------------------------------
def validar_seleccion_cliente(valor):
    if not valor:
        return True
    if valor not in OPCIONES_CLIENTE:
        return "Seleccione un cliente válido de la lista"
    return True

def validar_seleccion_robot(valor):
    if not valor:
        return True
    if valor not in OPCIONES_ROBOT:
        return "Seleccione un robot válido de la lista"
    return True

def validar_problema(valor):
    if not valor:
        return True
    if len(valor.strip()) < 5:
        return "El problema debe tener al menos 5 caracteres"
    if len(valor) > 300:
        return "El problema no puede exceder 300 caracteres"
    return True

# ----------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------
def _siguiente_id() -> int:
    return max((t["id"] for t in soporte_mock), default=0) + 1

def _nombre_cliente(nit: str) -> str:
    c = next((c for c in clientes_mock if c["nit"] == nit), None)
    return f"{nit} - {c['nombre']}" if c else nit

def _nombre_robot(id_robot: str) -> str:
    r = next((r for r in robots_mock if r["id"] == id_robot), None)
    return f"{id_robot} - {r['nombre']}" if r else id_robot

def _construir_filas() -> list:
    return [
        {
            "id": t["id"],
            "fecha_actualizacion": t.get("fecha_actualizacion", t.get("fecha_reporte", datetime.today().strftime("%Y-%m-%d"))),
            "cliente": _nombre_cliente(t["id_cliente"]),
            "robot": _nombre_robot(t["id_robot"]),
            "problema": t["problema"],
            "estado": t["estado"],
            "_id_cliente": t["id_cliente"],
            "_id_robot": t["id_robot"],
        }
        for t in soporte_mock
    ]

# ----------------------------------------------------------------------
# Operaciones de backend (conexión a Google Apps Script)
# ----------------------------------------------------------------------
def registrar_soporte_en_backend(datos: dict) -> dict:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {
        "action": "set_soportes_tecnicos",
        "id_cliente": datos["id_cliente"],
        "id_robot": datos["id_robot"],
        "problema": datos["problema"],
    }
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al registrar soporte"))
    return data

def actualizar_soporte_en_backend(id_soporte: str, datos: dict) -> dict:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "edit_soportes_tecnicos", "id_soporte": id_soporte}
    payload.update(datos)
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al actualizar soporte"))
    return data

def obtener_soportes_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_soportes_tecnicos", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener soportes"))
    return data.get("data", [])

def _obtener_clientes_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_clientes", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener clientes"))
    global clientes_mock
    data_list = data.get("data", [])
    if data_list:
        clientes_mock[:] = data_list
    return data_list

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

def _recargar_soportes_desde_backend(tabla_ref: SmartTable) -> None:
    if GAS_URL:
        try:
            _obtener_clientes_desde_backend()
            _obtener_robots_desde_backend()
            soportes = obtener_soportes_desde_backend()
            if soportes:
                soporte_mock[:] = soportes
        except Exception:
            ui.notify("No se pudo sincronizar con Apps Script; usando datos locales", type="warning")
    _reconstruir_catalogos()
    tabla_ref.set_data(_construir_filas())

async def _recargar_soportes_async(tabla_ref: SmartTable) -> None:
    if GAS_URL:
        try:
            await asyncio.to_thread(_obtener_clientes_desde_backend)
            await asyncio.to_thread(_obtener_robots_desde_backend)
            soportes = await asyncio.to_thread(obtener_soportes_desde_backend)
            if soportes:
                soporte_mock[:] = soportes
        except Exception:
            ui.notify("No se pudo sincronizar con Apps Script; usando datos locales", type="warning")
    _reconstruir_catalogos()
    tabla_ref.set_data(_construir_filas())

# ----------------------------------------------------------------------
# Página principal
# ----------------------------------------------------------------------
def page(content_container):
    with content_container:
        _loading = LoadingOverlay()
        _loading.build()

        if GAS_URL:
            async def _cargar():
                _loading.show()
                await asyncio.sleep(0.05)
                try:
                    await asyncio.to_thread(_obtener_clientes_desde_backend)
                    await asyncio.to_thread(_obtener_robots_desde_backend)
                    soportes = await asyncio.to_thread(obtener_soportes_desde_backend)
                    if soportes:
                        soporte_mock[:] = soportes
                except Exception:
                    ui.notify("No se pudieron cargar datos desde Apps Script", type="warning")
                finally:
                    _reconstruir_catalogos()
                    form.cliente.options = list(OPCIONES_CLIENTE)
                    form.robot.options = list(OPCIONES_ROBOT)
                    form.cliente.update()
                    form.robot.update()
                    tabla.set_data(_construir_filas())
                    _loading.hide()
            ui.timer(0.1, lambda: asyncio.ensure_future(_cargar()), once=True)
        else:
            _catalogos_desde_mock()

        ui.label("Gestión de Soporte Técnico").classes("page-title")
        ui.label("Registro y seguimiento de solicitudes").classes("page-subtitle").style("margin-bottom: 24px;")

        ui.label("Nueva solicitud de soporte").classes("text-h6").style("color: var(--teal-light); margin-bottom: 8px;")
        form = SmartForm(
            title="", subtitle="",
            padding="16px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar(form, tabla, _loading),
            submit_text="Registrar solicitud",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        form.cliente = form.add_field(
            "select", "Cliente",
            options=OPCIONES_CLIENTE,
            required=True,
            validation=validar_seleccion_cliente
        )
        form.cliente.props("use-input input-debounce=300 fill-input hide-selected")
        form.cliente.props('input-maxlength=80')

        form.robot = form.add_field(
            "select", "Robot",
            options=OPCIONES_ROBOT,
            required=True,
            validation=validar_seleccion_robot
        )
        form.robot.props("use-input input-debounce=300 fill-input hide-selected")
        form.robot.props('input-maxlength=80')

        form.problema = form.add_field(
            "textarea", "Problema reportado",
            rows=4,
            placeholder="Describa la falla o inconveniente...",
            required=True,
            max_length=300,
            validation=validar_problema
        )

        ui.separator().classes("my-6")
        ui.label("Listado de solicitudes").classes("text-h6").style("color: var(--teal-light); margin-bottom: 12px;")

        columnas = [
            {"label": "ID", "field": "id", "width": "60px", "filter_mode": "exact"},
            {"label": "Última act.", "field": "fecha_actualizacion", "width": "160px", "filter_mode": "startswith"},
            {"label": "Cliente", "field": "cliente", "width": "200px", "filter_mode": "contains"},
            {"label": "Robot", "field": "robot", "width": "180px", "filter_mode": "contains"},
            {"label": "Problema", "field": "problema", "width": "260px", "filter_mode": "contains"},
            {"label": "Estado", "field": "estado", "width": "120px", "filter_mode": "exact"},
        ]
        acciones = {
            "cambiar_estado": {"icon": "sync", "color": "teal", "tooltip": "Cambiar estado"},
        }
        tabla = SmartTable(
            columns=columnas,
            data=_construir_filas(),
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion(accion, fila, tabla, _loading),
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla.build()

# ----------------------------------------------------------------------
# Callbacks internos
# ----------------------------------------------------------------------
async def _registrar(f: SmartForm, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    nit_cliente = f.cliente.value.split(" - ")[0].strip()
    id_robot = f.robot.value.split(" - ")[0].strip()

    async def hacer():
        if GAS_URL:
            result = await asyncio.to_thread(
                registrar_soporte_en_backend,
                {
                    "id_cliente": nit_cliente,
                    "id_robot": id_robot,
                    "problema": f.problema.value.strip(),
                }
            )
            nuevo_id = result.get("id", "")
        else:
            nuevo_id = _siguiente_id()
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            soporte_mock.append({
                "id": nuevo_id,
                "fecha_reporte": fecha_hoy,
                "fecha_actualizacion": fecha_hoy,
                "problema": f.problema.value.strip(),
                "estado": "Abierto",
                "id_cliente": nit_cliente,
                "id_robot": id_robot,
            })
        ui.notify(f"✅ Solicitud #{nuevo_id} registrada — Estado: Abierto", type="positive", position="top")
        f.cliente.value = None
        f.robot.value = None
        f.problema.value = ""
        f.clear_errors()
        return nuevo_id

    async def refrescar():
        if GAS_URL:
            await _recargar_soportes_async(tabla_ref)
        else:
            tabla_ref.set_data(_construir_filas())

    await with_spinner(_loading, hacer, refresh=refrescar)

def _manejar_accion(accion: str, fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if accion == "cambiar_estado":
        _dialogo_cambiar_estado(fila, tabla_ref, _loading)

def _dialogo_cambiar_estado(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 420px; padding: 24px;"):
        ui.label(f"Cambiar estado — Ticket #{fila['id']}").classes("text-h6").style("color: var(--teal-light); margin-bottom: 4px;")
        ui.label(f"Problema: {fila['problema']}").style("color: var(--text-muted); font-size: 0.85rem; margin-bottom: 16px;")
        estado_actual = fila["estado"] if fila["estado"] in ESTADOS_TICKET else ESTADOS_TICKET[0]
        sel_estado = ui.select(options=ESTADOS_TICKET, label="Nuevo estado", value=estado_actual).classes("w-full")
        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def guardar():
                if not sel_estado.value:
                    ui.notify("Selecciona un estado", type="negative")
                    return

                async def editar():
                    if GAS_URL:
                        await asyncio.to_thread(
                            actualizar_soporte_en_backend,
                            str(fila["id"]),
                            {"estado": sel_estado.value}
                        )
                    else:
                        for ticket in soporte_mock:
                            if ticket["id"] == fila["id"]:
                                ticket["estado"] = sel_estado.value
                                ticket["fecha_actualizacion"] = datetime.today().strftime("%Y-%m-%d")
                                break
                    ui.notify(f"✅ Ticket #{fila['id']} → {sel_estado.value} (actualizado: {datetime.today().strftime('%Y-%m-%d')})", type="positive")
                    dialogo.close()

                async def refrescar():
                    if GAS_URL:
                        await _recargar_soportes_async(tabla_ref)
                    else:
                        tabla_ref.set_data(_construir_filas())

                await with_spinner(_loading, editar, refresh=refrescar)

            ui.button("Guardar cambio", on_click=guardar).props("unelevated color=teal")
    dialogo.open()
