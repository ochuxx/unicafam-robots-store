from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import empleados_mock
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
def _siguiente_id_empleado() -> int:
    return max((e["id"] for e in empleados_mock), default=1000) + 1

def registrar_empleado_en_backend_local(datos: dict) -> dict:
    nuevo_empleado = {
        "id":        _siguiente_id_empleado(),
        "nombre":    datos["nombre"],
        "cargo":     datos["cargo"],
        "correo":    datos["correo"],
        "telefono":  datos["telefono"],
    }
    empleados_mock.append(nuevo_empleado)
    return nuevo_empleado

def actualizar_empleado_en_backend_local(doc_empleado: str, datos: dict) -> bool:
    for i, emp in enumerate(empleados_mock):
        if str(emp["id"]) == str(doc_empleado):
            empleados_mock[i].update(datos)
            return True
    return False

def eliminar_empleado_en_backend_local(doc_empleado: str) -> bool:
    global empleados_mock
    longitud_anterior = len(empleados_mock)
    empleados_mock[:] = [e for e in empleados_mock if str(e["id"]) != str(doc_empleado)]
    return len(empleados_mock) < longitud_anterior

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (conexión a Google Apps Script)
# ──────────────────────────────────────────────────────────────────────
def registrar_empleado_en_backend(datos: dict) -> dict:
    if not GAS_URL:
        return registrar_empleado_en_backend_local(datos)
    payload = {
        "action": "set_empleados",
        "nombre": datos["nombre"],
        "cargo": datos["cargo"],
        "correo": datos["correo"],
        "telefono": datos["telefono"],
    }
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al registrar empleado"))
    return data

def actualizar_empleado_en_backend(id_empleado: str, datos: dict) -> bool:
    if not GAS_URL:
        return actualizar_empleado_en_backend_local(id_empleado, datos)
    payload = {"action": "edit_empleados", "id_empleado": id_empleado}
    payload.update(datos)
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al actualizar empleado"))
    return True

def eliminar_empleado_en_backend(id_empleado: str) -> bool:
    if not GAS_URL:
        return eliminar_empleado_en_backend_local(id_empleado)
    payload = {"action": "delete_empleados", "id_empleado": id_empleado}
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al eliminar empleado"))
    return True

def obtener_empleados_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_empleados", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener empleados"))
    return data.get("data", [])

async def _recargar_empleados_async(tabla_ref: SmartTable) -> None:
    if GAS_URL:
        try:
            empleados = await asyncio.to_thread(obtener_empleados_desde_backend)
            if empleados:
                empleados_mock[:] = empleados
        except Exception:
            ui.notify("No se pudo sincronizar con Apps Script; usando datos locales", type="warning")
    tabla_ref.set_data(empleados_mock)

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
                    empleados = await asyncio.to_thread(obtener_empleados_desde_backend)
                    if empleados:
                        empleados_mock[:] = empleados
                except Exception:
                    ui.notify("No se pudieron cargar datos desde Apps Script", type="warning")
                finally:
                    tabla_empleados.set_data(empleados_mock)
                    _loading.hide()
            ui.timer(0.1, lambda: asyncio.ensure_future(_cargar()), once=True)

        ui.label("Gestión de Empleados").classes("page-title")
        ui.label("Registro de personal").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        ui.label("Registrar nuevo empleado").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_empleado(form, tabla_empleados, _loading),
            submit_text="Guardar empleado",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        form.nombre = form.add_field(
            "input", "Nombre completo",
            placeholder="Nombres y apellidos",
            required=True,
            max_length=80
        )

        form.cargo = form.add_field(
            "input", "Cargo",
            placeholder="Ej: Vendedor, Técnico, Administrador",
            max_length=60
        )

        form.correo = form.add_field(
            "email", "Correo electrónico",
            placeholder="empleado@empresa.com",
            max_length=80
        )

        form.telefono = form.add_field(
            "input", "Teléfono",
            placeholder="300 000 0000",
            max_length=20
        )

        ui.separator().classes("my-6")

        ui.label("Listado de empleados").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        columnas_empleados = [
            {"label": "ID",            "field": "id",       "width": "100px", "filter_mode": "exact"},
            {"label": "Nombre",        "field": "nombre",   "width": "200px", "filter_mode": "contains"},
            {"label": "Cargo",         "field": "cargo",    "width": "150px", "filter_mode": "exact"},
            {"label": "Correo",        "field": "correo",   "width": "200px", "filter_mode": "contains"},
            {"label": "Teléfono",      "field": "telefono", "width": "150px", "filter_mode": "contains"},
        ]

        acciones = {
            "editar":   {"icon": "edit",   "color": "amber", "tooltip": "Editar empleado"},
            "eliminar": {"icon": "delete", "color": "red",   "tooltip": "Eliminar empleado"},
        }

        tabla_empleados = SmartTable(
            columns=columnas_empleados,
            data=empleados_mock,
            title="",
            subtitle="",
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion_empleado(accion, fila, tabla_empleados, _loading),
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla_empleados.build()

# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────
async def _registrar_empleado(f: SmartForm, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    datos = {
        "nombre":   f.nombre.value.strip(),
        "cargo":    (f.cargo.value or "").strip(),
        "correo":   (f.correo.value or "").strip(),
        "telefono": (f.telefono.value or "").strip(),
    }

    async def hacer():
        if GAS_URL:
            result = await asyncio.to_thread(registrar_empleado_en_backend, datos)
            nuevo_id = result.get("id", "")
        else:
            nuevo = registrar_empleado_en_backend_local(datos)
            nuevo_id = nuevo["id"]
        ui.notify(f"✅ Empleado {datos['nombre']} registrado (ID {nuevo_id})", type="positive")
        f.nombre.value = ""
        f.cargo.value = ""
        f.correo.value = ""
        f.telefono.value = ""
        f.clear_errors()
        return nuevo_id

    async def refrescar():
        await _recargar_empleados_async(tabla_ref)

    await with_spinner(_loading, hacer, refresh=refrescar, loading_after_action=True)

def _manejar_accion_empleado(accion: str, fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if accion == "editar":
        _abrir_dialogo_edicion_empleado(fila, tabla_ref, _loading)
    elif accion == "eliminar":
        _confirmar_eliminacion_empleado(fila, tabla_ref, _loading)

def _abrir_dialogo_edicion_empleado(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar empleado — ID {fila['id']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 16px;"
        )

        inp_nombre   = ui.input("Nombre completo", value=fila.get("nombre", "")).classes("w-full")
        inp_cargo    = ui.input("Cargo", value=fila.get("cargo", "")).classes("w-full")
        inp_correo   = ui.input("Correo electrónico", value=fila.get("correo", "")).classes("w-full")
        inp_telefono = ui.input("Teléfono", value=fila.get("telefono", "")).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def guardar():
                if not inp_nombre.value:
                    ui.notify("El nombre es obligatorio", type="negative")
                    return

                datos_actualizados = {
                    "nombre":   inp_nombre.value.strip(),
                    "cargo":    (inp_cargo.value or "").strip(),
                    "correo":   str(inp_correo.value or "").strip(),
                    "telefono": str(inp_telefono.value or "").strip(),
                }

                async def editar():
                    if GAS_URL:
                        await asyncio.to_thread(actualizar_empleado_en_backend, str(fila["id"]), datos_actualizados)
                    else:
                        actualizar_empleado_en_backend_local(str(fila["id"]), datos_actualizados)
                    ui.notify(f"✅ Empleado {datos_actualizados['nombre']} actualizado", type="positive")
                    dialogo.close()

                async def refrescar():
                    await _recargar_empleados_async(tabla_ref)

                await with_spinner(_loading, editar, refresh=refrescar, loading_after_action=True)

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()

def _confirmar_eliminacion_empleado(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar empleado").classes("text-h6").style(
            "color: #F44336; margin-bottom: 8px;"
        )
        ui.label(
            f"¿Estás seguro de que deseas eliminar a {fila['nombre']} "
            f"(ID {fila['id']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def confirmar():
                async def eliminar():
                    if GAS_URL:
                        await asyncio.to_thread(eliminar_empleado_en_backend, str(fila["id"]))
                    else:
                        eliminar_empleado_en_backend_local(str(fila["id"]))
                    ui.notify(f"🗑️ Empleado {fila['nombre']} eliminado", type="positive")
                    dialogo.close()

                async def refrescar():
                    await _recargar_empleados_async(tabla_ref)

                await with_spinner(_loading, eliminar, refresh=refrescar, loading_after_action=True)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()
