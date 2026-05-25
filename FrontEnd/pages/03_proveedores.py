from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import proveedores_mock
from components.loading import LoadingOverlay, with_spinner
from dotenv import load_dotenv
import os
import requests
import json
import asyncio

load_dotenv()
GAS_URL = os.getenv("GAS_URL", "").strip()

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────
def _siguiente_nit() -> str:
    nums = [int(p["nit"]) for p in proveedores_mock if p["nit"].isdigit()]
    return str(max(nums, default=900000000) + 1)

def registrar_proveedor_en_backend_local(datos: dict) -> dict:
    nuevo_proveedor = {
        "nit":            _siguiente_nit(),
        "nombre_empresa": datos["nombre_empresa"],
        "contacto":       datos["contacto"],
        "telefono":       datos["telefono"],
        "correo":         datos["correo"],
    }
    proveedores_mock.append(nuevo_proveedor)
    return nuevo_proveedor

def actualizar_proveedor_en_backend_local(nit_proveedor: str, datos: dict) -> bool:
    for i, prov in enumerate(proveedores_mock):
        if prov["nit"] == nit_proveedor:
            proveedores_mock[i].update(datos)
            return True
    return False

def eliminar_proveedor_en_backend_local(nit_proveedor: str) -> bool:
    global proveedores_mock
    longitud_anterior = len(proveedores_mock)
    proveedores_mock[:] = [p for p in proveedores_mock if p["nit"] != nit_proveedor]
    return len(proveedores_mock) < longitud_anterior

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (conexión a Google Apps Script)
# ──────────────────────────────────────────────────────────────────────
def registrar_proveedor_en_backend(datos: dict) -> dict:
    if not GAS_URL:
        return registrar_proveedor_en_backend_local(datos)
    payload = {
        "action": "set_proveedores",
        "nombre_empresa": datos["nombre_empresa"],
        "contacto": datos["contacto"],
        "telefono": datos["telefono"],
        "correo": datos["correo"],
    }
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al registrar proveedor"))
    return data

def actualizar_proveedor_en_backend(nit_proveedor: str, datos: dict) -> bool:
    if not GAS_URL:
        return actualizar_proveedor_en_backend_local(nit_proveedor, datos)
    payload = {"action": "edit_proveedores", "id_proveedor": nit_proveedor}
    payload.update(datos)
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al actualizar proveedor"))
    return True

def eliminar_proveedor_en_backend(nit_proveedor: str) -> bool:
    if not GAS_URL:
        return eliminar_proveedor_en_backend_local(nit_proveedor)
    payload = {"action": "delete_proveedores", "id_proveedor": nit_proveedor}
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al eliminar proveedor"))
    return True

def obtener_proveedores_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_proveedores", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener proveedores"))
    return data.get("data", [])

async def _recargar_proveedores_async(tabla_ref: SmartTable) -> None:
    if GAS_URL:
        try:
            proveedores = await asyncio.to_thread(obtener_proveedores_desde_backend)
            if proveedores:
                proveedores_mock[:] = proveedores
        except Exception:
            ui.notify("No se pudo sincronizar con Apps Script; usando datos locales", type="warning")
    tabla_ref.set_data(proveedores_mock)

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
                    proveedores = await asyncio.to_thread(obtener_proveedores_desde_backend)
                    if proveedores:
                        proveedores_mock[:] = proveedores
                except Exception:
                    ui.notify("No se pudieron cargar datos desde Apps Script", type="warning")
                finally:
                    tabla_proveedores.set_data(proveedores_mock)
                    _loading.hide()
            ui.timer(0.1, lambda: asyncio.ensure_future(_cargar()), once=True)

        ui.label("Gestión de Proveedores").classes("page-title")
        ui.label("Registro de empresas proveedoras de robots").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        ui.label("Registrar nuevo proveedor").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_proveedor(form, tabla_proveedores, _loading),
            submit_text="Guardar proveedor",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        form.nombre_empresa = form.add_field(
            "input", "Nombre empresa",
            placeholder="Ej: RoboTech S.A.S",
            required=True,
            max_length=80
        )

        form.contacto = form.add_field(
            "input", "Persona de contacto",
            placeholder="Nombre del representante",
            max_length=40
        )

        form.telefono = form.add_field(
            "input", "Teléfono",
            placeholder="300 000 0000",
            max_length=20
        )

        form.correo = form.add_field(
            "email", "Correo electrónico",
            placeholder="contacto@empresa.com",
            max_length=80
        )

        ui.separator().classes("my-6")

        ui.label("Listado de proveedores").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        columnas_proveedores = [
            {"label": "NIT",            "field": "nit",            "width": "140px", "filter_mode": "exact"},
            {"label": "Nombre empresa", "field": "nombre_empresa", "width": "200px", "filter_mode": "contains"},
            {"label": "Contacto",       "field": "contacto",       "width": "150px", "filter_mode": "contains"},
            {"label": "Teléfono",       "field": "telefono",       "width": "150px", "filter_mode": "contains"},
            {"label": "Correo",         "field": "correo",         "width": "200px", "filter_mode": "contains"},
        ]

        acciones = {
            "editar":   {"icon": "edit",   "color": "amber", "tooltip": "Editar proveedor"},
            "eliminar": {"icon": "delete", "color": "red",   "tooltip": "Eliminar proveedor"},
        }

        tabla_proveedores = SmartTable(
            columns=columnas_proveedores,
            data=proveedores_mock,
            title="",
            subtitle="",
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion_proveedor(accion, fila, tabla_proveedores, _loading),
            row_key="nit",
            max_height="500px",
            filterable=True,
        )
        tabla_proveedores.build()

# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────
async def _registrar_proveedor(f: SmartForm, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    datos = {
        "nombre_empresa": f.nombre_empresa.value.strip(),
        "contacto":       (f.contacto.value or "").strip(),
        "telefono":       (f.telefono.value or "").strip(),
        "correo":         (f.correo.value or "").strip(),
    }

    async def hacer():
        if GAS_URL:
            result = await asyncio.to_thread(registrar_proveedor_en_backend, datos)
            nuevo_id = result.get("id", "")
        else:
            nuevo = registrar_proveedor_en_backend_local(datos)
            nuevo_id = nuevo["nit"]
        ui.notify(f"✅ Proveedor {datos['nombre_empresa']} registrado (NIT {nuevo_id})", type="positive")
        f.nombre_empresa.value = ""
        f.contacto.value = ""
        f.telefono.value = ""
        f.correo.value = ""
        f.clear_errors()
        return nuevo_id

    async def refrescar():
        await _recargar_proveedores_async(tabla_ref)

    await with_spinner(_loading, hacer, refresh=refrescar, loading_after_action=True)

def _manejar_accion_proveedor(accion: str, fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if accion == "editar":
        _abrir_dialogo_edicion_proveedor(fila, tabla_ref, _loading)
    elif accion == "eliminar":
        _confirmar_eliminacion_proveedor(fila, tabla_ref, _loading)

def _abrir_dialogo_edicion_proveedor(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar proveedor — {fila['nit']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 16px;"
        )

        inp_nombre_empresa = ui.input("Nombre empresa", value=fila.get("nombre_empresa", "")).classes("w-full")
        inp_contacto       = ui.input("Persona de contacto", value=fila.get("contacto", "")).classes("w-full")
        inp_telefono       = ui.input("Teléfono", value=fila.get("telefono", "")).classes("w-full")
        inp_correo         = ui.input("Correo electrónico", value=fila.get("correo", "")).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def guardar():
                if not inp_nombre_empresa.value:
                    ui.notify("El nombre de la empresa es obligatorio", type="negative")
                    return

                datos_actualizados = {
                    "nombre_empresa": inp_nombre_empresa.value.strip(),
                    "contacto":       str(inp_contacto.value or "").strip(),
                    "telefono":       str(inp_telefono.value or "").strip(),
                    "correo":         str(inp_correo.value or "").strip(),
                }

                async def editar():
                    if GAS_URL:
                        await asyncio.to_thread(actualizar_proveedor_en_backend, fila["nit"], datos_actualizados)
                    else:
                        actualizar_proveedor_en_backend_local(fila["nit"], datos_actualizados)
                    ui.notify(f"✅ Proveedor {datos_actualizados['nombre_empresa']} actualizado", type="positive")
                    dialogo.close()

                async def refrescar():
                    await _recargar_proveedores_async(tabla_ref)

                await with_spinner(_loading, editar, refresh=refrescar, loading_after_action=True)

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()

def _confirmar_eliminacion_proveedor(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar proveedor").classes("text-h6").style(
            "color: #F44336; margin-bottom: 8px;"
        )
        ui.label(
            f"¿Estás seguro de que deseas eliminar el proveedor '{fila['nombre_empresa']}' "
            f"(NIT {fila['nit']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def confirmar():
                async def eliminar():
                    if GAS_URL:
                        await asyncio.to_thread(eliminar_proveedor_en_backend, fila["nit"])
                    else:
                        eliminar_proveedor_en_backend_local(fila["nit"])
                    ui.notify(f"🗑️ Proveedor {fila['nombre_empresa']} eliminado", type="positive")
                    dialogo.close()

                async def refrescar():
                    await _recargar_proveedores_async(tabla_ref)

                await with_spinner(_loading, eliminar, refresh=refrescar, loading_after_action=True)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()
