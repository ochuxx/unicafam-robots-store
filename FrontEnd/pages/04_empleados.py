# FrontEnd/pages/04_empleados.py
from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import empleados_mock

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────

def registrar_empleado_en_backend(datos: dict) -> dict:
    nuevo_empleado = {
        "id":        datos["documento"],
        "nombre":    datos["nombre"],
        "cargo":     datos["cargo"],
        "correo":    datos["correo"],
        "telefono":  datos["telefono"],
    }
    empleados_mock.append(nuevo_empleado)
    return nuevo_empleado


def actualizar_empleado_en_backend(doc_empleado: str, datos: dict) -> bool:
    for i, emp in enumerate(empleados_mock):
        if emp["id"] == doc_empleado:
            empleados_mock[i].update(datos)
            return True
    return False


def eliminar_empleado_en_backend(doc_empleado: str) -> bool:
    global empleados_mock
    longitud_anterior = len(empleados_mock)
    empleados_mock[:] = [e for e in empleados_mock if e["id"] != doc_empleado]
    return len(empleados_mock) < longitud_anterior


# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────

def page(content_container):
    with content_container:
        ui.label("Gestión de Empleados").classes("page-title")
        ui.label("Registro de personal").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        # ── Formulario de registro ───────────────────────────────────
        ui.label("Registrar nuevo empleado").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_empleado(form, tabla_empleados),
            submit_text="Guardar empleado",
        )
        form.build()

        # Campos del formulario
        form.documento = form.add_field("input", "Documento de identidad", placeholder="Ej: 12345678", required=True)
        form.nombre    = form.add_field("input", "Nombre completo", placeholder="Nombres y apellidos")
        form.cargo     = form.add_field("input", "Cargo", placeholder="Ej: Vendedor, Técnico, Administrador")
        form.correo    = form.add_field("email", "Correo electrónico", placeholder="empleado@empresa.com")
        form.telefono  = form.add_field("input", "Teléfono", placeholder="300 000 0000")

        ui.separator().classes("my-6")

        # ── Tabla de empleados ───────────────────────────────────────
        ui.label("Listado de empleados").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        columnas_empleados = [
            {"label": "Documento",     "field": "id",       "width": "100px", "filter_mode": "exact"},
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
            on_action=lambda accion, fila: _manejar_accion_empleado(accion, fila, tabla_empleados),
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla_empleados.build()


# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────

def _registrar_empleado(f: SmartForm, tabla_ref: SmartTable) -> None:
    """Valida el formulario, persiste el empleado y refresca la tabla."""
    if not f.documento.value or not f.nombre.value:
        ui.notify("Documento de identidad y nombre son obligatorios", type="negative")
        return

    datos = {
        "documento": f.documento.value.strip(),
        "nombre":    f.nombre.value.strip(),
        "cargo":     (f.cargo.value or "").strip(),
        "correo":    (f.correo.value or "").strip(),
        "telefono":  (f.telefono.value or "").strip(),
    }

    # Verificar documento duplicado
    docs_existentes = {e["id"] for e in empleados_mock}
    if datos["documento"] in docs_existentes:
        ui.notify(f"Ya existe un empleado con documento {datos['documento']}", type="warning")
        return

    nuevo = registrar_empleado_en_backend(datos)
    ui.notify(
        f"✅ Empleado {nuevo['nombre']} registrado (Documento {nuevo['id']})",
        type="positive",
    )

    # Limpiar formulario
    f.documento.value = ""
    f.nombre.value = ""
    f.cargo.value = ""
    f.correo.value = ""
    f.telefono.value = ""

    tabla_ref.set_data(empleados_mock)


def _manejar_accion_empleado(accion: str, fila: dict, tabla_ref: SmartTable) -> None:
    """Despachador de acciones de la tabla."""
    if accion == "editar":
        _abrir_dialogo_edicion_empleado(fila, tabla_ref)
    elif accion == "eliminar":
        _confirmar_eliminacion_empleado(fila, tabla_ref)


def _abrir_dialogo_edicion_empleado(fila: dict, tabla_ref: SmartTable) -> None:
    """Abre un diálogo modal con los datos del empleado para editarlos."""
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar empleado — {fila['id']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 16px;"
        )

        inp_nombre   = ui.input("Nombre completo", value=fila.get("nombre", "")).classes("w-full")
        inp_cargo    = ui.input("Cargo", value=fila.get("cargo", "")).classes("w-full")
        inp_correo   = ui.input("Correo electrónico", value=fila.get("correo", "")).classes("w-full")
        inp_telefono = ui.input("Teléfono", value=fila.get("telefono", "")).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def guardar():
                if not inp_nombre.value:
                    ui.notify("El nombre es obligatorio", type="negative")
                    return

                datos_actualizados = {
                    "nombre":   inp_nombre.value.strip(),
                    "cargo":    (inp_cargo.value or "").strip(),
                    "correo":   (inp_correo.value or "").strip(),
                    "telefono": (inp_telefono.value or "").strip(),
                }
                ok = actualizar_empleado_en_backend(fila["id"], datos_actualizados)
                if ok:
                    ui.notify(
                        f"✅ Empleado {datos_actualizados['nombre']} actualizado",
                        type="positive",
                    )
                    tabla_ref.set_data(empleados_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el empleado para actualizar", type="negative")

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()


def _confirmar_eliminacion_empleado(fila: dict, tabla_ref: SmartTable) -> None:
    """Abre un diálogo de confirmación antes de eliminar el empleado."""
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar empleado").classes("text-h6").style(
            "color: #F44336; margin-bottom: 8px;"
        )
        ui.label(
            f"¿Estás seguro de que deseas eliminar a {fila['nombre']} "
            f"(Documento {fila['id']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def confirmar():
                ok = eliminar_empleado_en_backend(fila["id"])
                if ok:
                    ui.notify(
                        f"🗑️ Empleado {fila['nombre']} eliminado",
                        type="positive",
                    )
                    tabla_ref.set_data(empleados_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el empleado para eliminar", type="negative")

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()