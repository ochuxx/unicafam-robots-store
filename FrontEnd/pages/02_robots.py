from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import robots_mock
import re
from components.loading import LoadingOverlay, with_spinner

# ──────────────────────────────────────────────────────────────────────
# Función de validación personalizada para el número de serie (único + formato)
# ──────────────────────────────────────────────────────────────────────
def validar_serie_robot(valor):
    """Valida que el número de serie no esté vacío y tenga un formato básico."""
    if not valor:
        return True  # El required se encarga
    # Ejemplo: permite letras, números, guiones y guiones bajos (mínimo 3 caracteres)
    if not re.match(r'^[A-Za-z0-9\-_]{3,20}$', valor):
        return "El número de serie debe tener entre 3 y 20 caracteres (letras, números, guiones o guión bajo)"
    # La unicidad se verificará aparte en el callback (no se puede validar aquí porque depende de la BD)
    return True

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────
def registrar_robot_en_backend(datos: dict) -> dict:
    nuevo_robot = {
        "id":          datos["id"],
        "nombre":      datos["nombre"],
        "descripcion": datos["descripcion"],
        "tipo":        datos["tipo"],
    }
    robots_mock.append(nuevo_robot)
    return nuevo_robot

def actualizar_robot_en_backend(id_robot: str, datos: dict) -> bool:
    for i, robot in enumerate(robots_mock):
        if robot["id"] == id_robot:
            robots_mock[i].update(datos)
            return True
    return False

def eliminar_robot_en_backend(id_robot: str) -> bool:
    global robots_mock
    longitud_anterior = len(robots_mock)
    robots_mock[:] = [r for r in robots_mock if r["id"] != id_robot]
    return len(robots_mock) < longitud_anterior

# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────
TIPOS_ROBOT = ["Doméstico", "Industrial", "Educativo", "Médico", "Comercial", "Seguridad", "Hogar"]

def page(content_container):
    with content_container:
        _loading = LoadingOverlay()
        _loading.build()

        ui.label("Gestión de Robots").classes("page-title")
        ui.label("Registro y catálogo de robots").classes("page-subtitle").style("margin-bottom: 24px;")

        ui.label("Registrar nuevo robot").classes("text-h6").style("color: var(--teal-light);")

        # Formulario con validación manual
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_robot(form, tabla_robots, _loading),
            submit_text="Guardar robot",
            enable_validation=True,
            max_length=100,   # límite global para textos
        )
        form.build()

        # Campo: número de serie (ID único)
        form.id_robot = form.add_field(
            "input", "Número de serie",
            placeholder="Ej: RB-2024-001",
            required=True,
            max_length=20,
            validation=validar_serie_robot
        )
        # Opcional: teclado en móviles (no necesario, pero se puede dejar)
        form.id_robot.props('inputmode=text')

        # Campo: nombre del robot
        form.nombre = form.add_field(
            "input", "Nombre del robot",
            placeholder="Ej: HomeBot X2",
            required=True,
            max_length=30
        )

        # Campo: descripción (textarea)
        form.descripcion = form.add_field(
            "textarea", "Descripción",
            rows=3,
            placeholder="Funcionalidades y características",
            max_length=300   # Límite específico para descripción larga
        )

        # Campo: tipo (select)
        form.tipo = form.add_field(
            "select", "Tipo",
            options=TIPOS_ROBOT,
            required=True
        )

        ui.separator().classes("my-6")

        ui.label("Listado de robots").classes("text-h6").style("color: var(--teal-light);")

        columnas_robots = [
            {"label": "Número de serie", "field": "id",          "width": "150px", "filter_mode": "exact"},
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
        "id":          f.id_robot.value.strip(),
        "nombre":      f.nombre.value.strip(),
        "descripcion": (f.descripcion.value or "").strip(),
        "tipo":        f.tipo.value,
    }

    if any(r["id"] == datos["id"] for r in robots_mock):
        ui.notify(f"Ya existe un robot con número de serie {datos['id']}", type="warning")
        return

    def hacer():
        nuevo = registrar_robot_en_backend(datos)
        ui.notify(f"✅ Robot {nuevo['nombre']} registrado (Serie {nuevo['id']})", type="positive")
        f.id_robot.value = ""
        f.nombre.value = ""
        f.descripcion.value = ""
        f.tipo.value = None
        f.clear_errors()
        return nuevo

    def refrescar():
        tabla_ref.set_data(robots_mock)

    await with_spinner(_loading, hacer, refresh=refrescar)

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

                def editar():
                    ok = actualizar_robot_en_backend(fila["id"], datos_actualizados)
                    if ok:
                        ui.notify(f"✅ Robot {datos_actualizados['nombre']} actualizado", type="positive")
                        dialogo.close()
                    else:
                        ui.notify("No se encontró el robot para actualizar", type="negative")
                    return ok

                def refrescar():
                    tabla_ref.set_data(robots_mock)

                await with_spinner(_loading, editar, refresh=refrescar)

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")
    dialogo.open()

def _confirmar_eliminacion_robot(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar robot").classes("text-h6").style("color: #F44336; margin-bottom: 8px;")
        ui.label(
            f"¿Estás seguro de que deseas eliminar el robot '{fila['nombre']}' "
            f"(Serie {fila['id']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")
        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            async def confirmar():
                def eliminar():
                    ok = eliminar_robot_en_backend(fila["id"])
                    if ok:
                        ui.notify(f"🗑️ Robot {fila['nombre']} eliminado", type="positive")
                        dialogo.close()
                    else:
                        ui.notify("No se encontró el robot para eliminar", type="negative")
                    return ok

                def refrescar():
                    tabla_ref.set_data(robots_mock)

                await with_spinner(_loading, eliminar, refresh=refrescar)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")
    dialogo.open()