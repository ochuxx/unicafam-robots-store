from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import robots_mock
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
def _siguiente_id_robot() -> str:
    return f"SER-{max((int(r['id'].split('-')[1]) for r in robots_mock if '-' in r['id']), default=0) + 1:04d}"

def registrar_robot_en_backend_local(datos: dict) -> dict:
    nuevo_robot = {
        "id":          _siguiente_id_robot(),
        "nombre":      datos["nombre"],
        "descripcion": datos["descripcion"],
        "tipo":        datos["tipo"],
    }
    robots_mock.append(nuevo_robot)
    return nuevo_robot

def actualizar_robot_en_backend_local(id_robot: str, datos: dict) -> bool:
    for i, robot in enumerate(robots_mock):
        if robot["id"] == id_robot:
            robots_mock[i].update(datos)
            return True
    return False

def eliminar_robot_en_backend_local(id_robot: str) -> bool:
    global robots_mock
    longitud_anterior = len(robots_mock)
    robots_mock[:] = [r for r in robots_mock if r["id"] != id_robot]
    return len(robots_mock) < longitud_anterior

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (conexión a Google Apps Script)
# ──────────────────────────────────────────────────────────────────────
def registrar_robot_en_backend(datos: dict) -> dict:
    if not GAS_URL:
        return registrar_robot_en_backend_local(datos)
    payload = {
        "action": "set_robots",
        "nombre_robot": datos["nombre"],
        "descripcion": datos["descripcion"],
        "tipo": datos["tipo"],
    }
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al registrar robot"))
    return data

def actualizar_robot_en_backend(id_robot: str, datos: dict) -> bool:
    if not GAS_URL:
        return actualizar_robot_en_backend_local(id_robot, datos)
    payload = {"action": "edit_robots", "id_robot": id_robot}
    payload.update(datos)
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al actualizar robot"))
    return True

def eliminar_robot_en_backend(id_robot: str) -> bool:
    if not GAS_URL:
        return eliminar_robot_en_backend_local(id_robot)
    payload = {"action": "delete_robots", "id_robot": id_robot}
    response = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al eliminar robot"))
    return True

def obtener_robots_desde_backend(limit: int = 500) -> list:
    if not GAS_URL:
        raise RuntimeError("GAS_URL no configurada")
    payload = {"action": "get_robots", "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", "Error al obtener robots"))
    return data.get("data", [])

async def _recargar_robots_async(tabla_ref: SmartTable) -> None:
    if GAS_URL:
        try:
            robots = await asyncio.to_thread(obtener_robots_desde_backend)
            if robots:
                robots_mock[:] = robots
        except Exception:
            ui.notify("No se pudo sincronizar con Apps Script; usando datos locales", type="warning")
    tabla_ref.set_data(robots_mock)

# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────
TIPOS_ROBOT = ["Doméstico", "Industrial", "Educativo", "Médico", "Comercial", "Seguridad", "Hogar"]

def page(content_container):
    with content_container:
        _loading = LoadingOverlay()
        _loading.build()

        if GAS_URL:
            async def _cargar():
                _loading.show()
                await asyncio.sleep(0.05)
                try:
                    robots = await asyncio.to_thread(obtener_robots_desde_backend)
                    if robots:
                        robots_mock[:] = robots
                except Exception:
                    ui.notify("No se pudieron cargar datos desde Apps Script", type="warning")
                finally:
                    tabla_robots.set_data(robots_mock)
                    _loading.hide()
            ui.timer(0.1, lambda: asyncio.ensure_future(_cargar()), once=True)

        ui.label("Gestión de Robots").classes("page-title")
        ui.label("Registro y catálogo de robots").classes("page-subtitle").style("margin-bottom: 24px;")

        ui.label("Registrar nuevo robot").classes("text-h6").style("color: var(--teal-light);")

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_robot(form, tabla_robots, _loading),
            submit_text="Guardar robot",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        form.nombre = form.add_field(
            "input", "Nombre del robot",
            placeholder="Ej: HomeBot X2",
            required=True,
            max_length=30
        )

        form.descripcion = form.add_field(
            "textarea", "Descripción",
            rows=3,
            placeholder="Funcionalidades y características",
            max_length=300
        )

        form.tipo = form.add_field(
            "select", "Tipo",
            options=TIPOS_ROBOT,
            required=True
        )

        ui.separator().classes("my-6")

        ui.label("Listado de robots").classes("text-h6").style("color: var(--teal-light);")

        columnas_robots = [
            {"label": "ID",               "field": "id",          "width": "150px", "filter_mode": "exact"},
            {"label": "Nombre",          "field": "nombre",      "width": "200px", "filter_mode": "contains"},
            {"label": "Descripción",     "field": "descripcion", "width": "300px", "filter_mode": "contains"},
            {"label": "Tipo",            "field": "tipo",        "width": "150px", "filter_mode": "exact"},
        ]

        acciones = {
            "editar":   {"icon": "edit",   "color": "amber", "tooltip": "Editar robot"},
            "eliminar": {"icon": "delete", "color": "red",   "tooltip": "Eliminar robot"},
        }

        tabla_robots = SmartTable(
            columns=columnas_robots,
            data=robots_mock,
            title="",
            subtitle="",
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion_robot(accion, fila, tabla_robots, _loading),
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla_robots.build()

# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────
async def _registrar_robot(f: SmartForm, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    datos = {
        "nombre":      f.nombre.value.strip(),
        "descripcion": (f.descripcion.value or "").strip(),
        "tipo":        f.tipo.value,
    }

    async def hacer():
        if GAS_URL:
            result = await asyncio.to_thread(registrar_robot_en_backend, datos)
            nuevo_id = result.get("id", "")
        else:
            nuevo = registrar_robot_en_backend_local(datos)
            nuevo_id = nuevo["id"]
        ui.notify(f"✅ Robot registrado (ID {nuevo_id})", type="positive")
        f.nombre.value = ""
        f.descripcion.value = ""
        f.tipo.value = None
        f.clear_errors()
        return nuevo_id

    async def refrescar():
        await _recargar_robots_async(tabla_ref)

    await with_spinner(_loading, hacer, refresh=refrescar, loading_after_action=True)

def _manejar_accion_robot(accion: str, fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if accion == "editar":
        _abrir_dialogo_edicion_robot(fila, tabla_ref, _loading)
    elif accion == "eliminar":
        _confirmar_eliminacion_robot(fila, tabla_ref, _loading)

def _abrir_dialogo_edicion_robot(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar robot — {fila['id']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 16px;"
        )

        inp_nombre      = ui.input("Nombre del robot", value=fila.get("nombre", "")).classes("w-full")
        inp_descripcion = ui.textarea("Descripción",   value=fila.get("descripcion", "")).classes("w-full")
        inp_tipo        = ui.select(options=TIPOS_ROBOT, label="Tipo", value=fila.get("tipo", "")).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def guardar():
                if not inp_nombre.value or not inp_tipo.value:
                    ui.notify("Nombre y Tipo son obligatorios", type="negative")
                    return
                datos_actualizados = {
                    "nombre":      inp_nombre.value.strip(),
                    "descripcion": inp_descripcion.value.strip(),
                    "tipo":        inp_tipo.value,
                }

                async def editar():
                    if GAS_URL:
                        await asyncio.to_thread(actualizar_robot_en_backend, fila["id"], datos_actualizados)
                    else:
                        actualizar_robot_en_backend_local(fila["id"], datos_actualizados)
                    ui.notify(f"✅ Robot {datos_actualizados['nombre']} actualizado", type="positive")
                    dialogo.close()

                async def refrescar():
                    await _recargar_robots_async(tabla_ref)

                await with_spinner(_loading, editar, refresh=refrescar, loading_after_action=True)

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")
    dialogo.open()

def _confirmar_eliminacion_robot(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar robot").classes("text-h6").style("color: #F44336; margin-bottom: 8px;")
        ui.label(
            f"¿Estás seguro de que deseas eliminar el robot '{fila['nombre']}' "
            f"(ID {fila['id']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")
        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def confirmar():
                async def eliminar():
                    if GAS_URL:
                        await asyncio.to_thread(eliminar_robot_en_backend, fila["id"])
                    else:
                        eliminar_robot_en_backend_local(fila["id"])
                    ui.notify(f"🗑️ Robot {fila['nombre']} eliminado", type="positive")
                    dialogo.close()

                async def refrescar():
                    await _recargar_robots_async(tabla_ref)

                await with_spinner(_loading, eliminar, refresh=refrescar, loading_after_action=True)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")
    dialogo.open()
