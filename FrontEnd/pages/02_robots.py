# FrontEnd/pages/02_robots.py
from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import robots_mock


# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────

def registrar_robot_en_backend(datos: dict) -> dict:
    """
    Agrega un nuevo robot a la base de datos mock (robots_mock).

    :param datos: Diccionario con las claves: id, nombre, descripcion, tipo.
    :return: El diccionario del robot recién creado.
    """
    nuevo_robot = {
        "id":          datos["id"],
        "nombre":      datos["nombre"],
        "descripcion": datos["descripcion"],
        "tipo":        datos["tipo"],
    }
    robots_mock.append(nuevo_robot)
    return nuevo_robot


def actualizar_robot_en_backend(id_robot: str, datos: dict) -> bool:
    """
    Actualiza los datos de un robot existente en robots_mock.

    :param id_robot: Número de serie (id) del robot a actualizar.
    :param datos: Diccionario con los campos a actualizar (nombre, descripcion, tipo).
    :return: True si se encontró y actualizó, False en caso contrario.
    """
    for i, robot in enumerate(robots_mock):
        if robot["id"] == id_robot:
            robots_mock[i].update(datos)
            return True
    return False


def eliminar_robot_en_backend(id_robot: str) -> bool:
    """
    Elimina un robot de robots_mock por su número de serie.

    :param id_robot: Número de serie (id) del robot a eliminar.
    :return: True si se eliminó al menos un robot, False si no se encontró.
    """
    global robots_mock
    longitud_anterior = len(robots_mock)
    robots_mock[:] = [r for r in robots_mock if r["id"] != id_robot]
    return len(robots_mock) < longitud_anterior


# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────

TIPOS_ROBOT = ["Doméstico", "Industrial", "Educativo", "Médico", "Comercial", "Seguridad", "Hogar"]


def page(content_container):
    """
    Renderiza la página de gestión de robots en el contenedor proporcionado.

    Incluye:
    - Formulario de registro (SmartForm con 2 columnas).
    - Tabla de robots (SmartTable) con acciones editar/eliminar.
    - Diálogos para edición y confirmación de eliminación.

    :param content_container: Contenedor (ui.column) donde se montará la página.
    """
    with content_container:
        ui.label("Gestión de Robots").classes("page-title")
        ui.label("Registro y catálogo de robots").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        # ── Formulario de registro ───────────────────────────────────
        ui.label("Registrar nuevo robot").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_robot(form, tabla_robots),
            submit_text="Guardar robot",
        )
        form.build()

        form.id_robot    = form.add_field("input",    "Número de serie",  placeholder="Ej: RB-2024-001")
        form.nombre      = form.add_field("input",    "Nombre del robot", placeholder="Ej: HomeBot X2")
        form.descripcion = form.add_field("textarea", "Descripción",      rows=3, placeholder="Funcionalidades y características")
        form.tipo        = form.add_field("select",   "Tipo",             options=TIPOS_ROBOT)

        ui.separator().classes("my-6")

        # ── Tabla de robots ──────────────────────────────────────────
        ui.label("Listado de robots").classes("text-h6").style(
            "color: var(--teal-light);"
        )

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
            on_action=lambda accion, fila: _manejar_accion_robot(accion, fila, tabla_robots),
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla_robots.build()


# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────

def _registrar_robot(f: SmartForm, tabla_ref: SmartTable) -> None:
    """
    Callback del botón Guardar robot. Valida el formulario, persiste el robot
    y refresca la tabla.

    :param f: Instancia del SmartForm con los campos.
    :param tabla_ref: Referencia a la SmartTable para actualizar los datos.
    """
    if not f.id_robot.value or not f.nombre.value or not f.tipo.value:
        ui.notify("Número de serie, nombre y tipo son obligatorios", type="negative")
        return

    datos = {
        "id":          f.id_robot.value.strip(),
        "nombre":      f.nombre.value.strip(),
        "descripcion": (f.descripcion.value or "").strip(),
        "tipo":        f.tipo.value,
    }

    ids_existentes = {r["id"] for r in robots_mock}
    if datos["id"] in ids_existentes:
        ui.notify(f"Ya existe un robot con número de serie {datos['id']}", type="warning")
        return

    nuevo = registrar_robot_en_backend(datos)
    ui.notify(f"✅ Robot {nuevo['nombre']} registrado (Serie {nuevo['id']})", type="positive")

    f.id_robot.value = f.nombre.value = f.descripcion.value = ""
    f.tipo.value = None

    tabla_ref.set_data(robots_mock)


def _manejar_accion_robot(accion: str, fila: dict, tabla_ref: SmartTable) -> None:
    """
    Despachador de acciones de la tabla de robots.

    :param accion: Nombre de la acción ('editar' o 'eliminar').
    :param fila: Diccionario con los datos del robot.
    :param tabla_ref: Referencia a la SmartTable para actualizar después de cambios.
    """
    if accion == "editar":
        _abrir_dialogo_edicion_robot(fila, tabla_ref)
    elif accion == "eliminar":
        _confirmar_eliminacion_robot(fila, tabla_ref)


def _abrir_dialogo_edicion_robot(fila: dict, tabla_ref: SmartTable) -> None:
    """
    Abre un diálogo modal con los datos del robot para editarlos.

    :param fila: Datos actuales del robot.
    :param tabla_ref: Referencia a la tabla para refrescar después de guardar.
    """
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar robot — {fila['id']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 16px;"
        )

        inp_nombre      = ui.input("Nombre del robot", value=fila.get("nombre", "")).classes("w-full")
        inp_descripcion = ui.textarea("Descripción",   value=fila.get("descripcion", "")).classes("w-full")

        # ✅ CORRECTO: options y label como keywords, nunca dos posicionales
        inp_tipo = ui.select(
            options=TIPOS_ROBOT,
            label="Tipo",
            value=fila.get("tipo", ""),
        ).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def guardar():
                if not inp_nombre.value or not inp_tipo.value:
                    ui.notify("Nombre y Tipo son obligatorios", type="negative")
                    return
                datos_actualizados = {
                    "nombre":      inp_nombre.value.strip(),
                    "descripcion": inp_descripcion.value.strip(),
                    "tipo":        inp_tipo.value,
                }
                ok = actualizar_robot_en_backend(fila["id"], datos_actualizados)
                if ok:
                    ui.notify(f"✅ Robot {datos_actualizados['nombre']} actualizado", type="positive")
                    tabla_ref.set_data(robots_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el robot para actualizar", type="negative")

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()


def _confirmar_eliminacion_robot(fila: dict, tabla_ref: SmartTable) -> None:
    """
    Abre un diálogo de confirmación antes de eliminar el robot.

    :param fila: Datos del robot a eliminar.
    :param tabla_ref: Referencia a la tabla para refrescar después de eliminar.
    """
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar robot").classes("text-h6").style(
            "color: #F44336; margin-bottom: 8px;"
        )
        ui.label(
            f"¿Estás seguro de que deseas eliminar el robot '{fila['nombre']}' "
            f"(Serie {fila['id']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def confirmar():
                ok = eliminar_robot_en_backend(fila["id"])
                if ok:
                    ui.notify(f"🗑️ Robot {fila['nombre']} eliminado", type="positive")
                    tabla_ref.set_data(robots_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el robot para eliminar", type="negative")

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()