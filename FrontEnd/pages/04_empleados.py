from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import empleados_mock
import re
from components.loading import LoadingOverlay, with_spinner

# ──────────────────────────────────────────────────────────────────────
# Función de validación personalizada para el documento (solo dígitos)
# ──────────────────────────────────────────────────────────────────────
def solo_digitos_documento(valor):
    """Valida que el documento de identidad contenga solo dígitos."""
    if not valor:
        return True
    if not re.match(r'^\d+$', valor):
        return "El documento solo puede contener números (sin puntos, guiones ni espacios)"
    return True

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
        _loading = LoadingOverlay()
        _loading.build()

        ui.label("Gestión de Empleados").classes("page-title")
        ui.label("Registro de personal").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        ui.label("Registrar nuevo empleado").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        # Formulario con validación manual
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_empleado(form, tabla_empleados, _loading),
            submit_text="Guardar empleado",
            enable_validation=True,
            max_length=100,   # límite global para textos
        )
        form.build()

        # Campo: documento (único)
        form.documento = form.add_field(
            "input", "Documento de identidad",
            placeholder="12345678",
            required=True,
            max_length=15,
            validation=solo_digitos_documento
        )
        form.documento.props('inputmode=numeric')  # teclado numérico en móviles

        # Campo: nombre completo
        form.nombre = form.add_field(
            "input", "Nombre completo",
            placeholder="Nombres y apellidos",
            required=True,
            max_length=80
        )

        # Campo: cargo
        form.cargo = form.add_field(
            "input", "Cargo",
            placeholder="Ej: Vendedor, Técnico, Administrador",
            max_length=60
        )

        # Campo: correo electrónico
        form.correo = form.add_field(
            "email", "Correo electrónico",
            placeholder="empleado@empresa.com",
            max_length=80
        )

        # Campo: teléfono
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
        "documento": f.documento.value.strip(),
        "nombre":    f.nombre.value.strip(),
        "cargo":     (f.cargo.value or "").strip(),
        "correo":    (f.correo.value or "").strip(),
        "telefono":  (f.telefono.value or "").strip(),
    }

    if any(e["id"] == datos["documento"] for e in empleados_mock):
        ui.notify(f"Ya existe un empleado con documento {datos['documento']}", type="warning")
        return

    def hacer():
        nuevo = registrar_empleado_en_backend(datos)
        ui.notify(
            f"✅ Empleado {nuevo['nombre']} registrado (Documento {nuevo['id']})",
            type="positive",
        )
        f.documento.value = ""
        f.nombre.value = ""
        f.cargo.value = ""
        f.correo.value = ""
        f.telefono.value = ""
        f.clear_errors()
        return nuevo

    def refrescar():
        tabla_ref.set_data(empleados_mock)

    await with_spinner(_loading, hacer, refresh=refrescar)

def _manejar_accion_empleado(accion: str, fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
    if accion == "editar":
        _abrir_dialogo_edicion_empleado(fila, tabla_ref, _loading)
    elif accion == "eliminar":
        _confirmar_eliminacion_empleado(fila, tabla_ref, _loading)

def _abrir_dialogo_edicion_empleado(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
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

            async def guardar():
                if not inp_nombre.value:
                    ui.notify("El nombre es obligatorio", type="negative")
                    return

                datos_actualizados = {
                    "nombre":   inp_nombre.value.strip(),
                    "cargo":    (inp_cargo.value or "").strip(),
                    "correo":   (inp_correo.value or "").strip(),
                    "telefono": (inp_telefono.value or "").strip(),
                }

                def editar():
                    ok = actualizar_empleado_en_backend(fila["id"], datos_actualizados)
                    if ok:
                        ui.notify(
                            f"✅ Empleado {datos_actualizados['nombre']} actualizado",
                            type="positive",
                        )
                        dialogo.close()
                    else:
                        ui.notify("No se encontró el empleado para actualizar", type="negative")
                    return ok

                def refrescar():
                    tabla_ref.set_data(empleados_mock)

                await with_spinner(_loading, editar, refresh=refrescar)

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()

def _confirmar_eliminacion_empleado(fila: dict, tabla_ref: SmartTable, _loading: LoadingOverlay) -> None:
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

            async def confirmar():
                def eliminar():
                    ok = eliminar_empleado_en_backend(fila["id"])
                    if ok:
                        ui.notify(
                            f"🗑️ Empleado {fila['nombre']} eliminado",
                            type="positive",
                        )
                        dialogo.close()
                    else:
                        ui.notify("No se encontró el empleado para eliminar", type="negative")
                    return ok

                def refrescar():
                    tabla_ref.set_data(empleados_mock)

                await with_spinner(_loading, eliminar, refresh=refrescar)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()