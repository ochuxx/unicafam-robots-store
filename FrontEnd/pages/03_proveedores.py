from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import proveedores_mock
import re
from components.loading import LoadingOverlay, with_spinner

# ──────────────────────────────────────────────────────────────────────
# Función de validación personalizada para el NIT (solo dígitos)
# ──────────────────────────────────────────────────────────────────────
def solo_digitos_nit(valor):
    """Valida que el NIT contenga solo dígitos (sin guiones, puntos ni espacios)."""
    if not valor:
        return True
    if not re.match(r'^\d+$', valor):
        return "El NIT solo puede contener números (sin puntos, guiones ni espacios)"
    return True

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────
def registrar_proveedor_en_backend(datos: dict) -> dict:
    nuevo_proveedor = {
        "nit":            datos["nit"],
        "nombre_empresa": datos["nombre_empresa"],
        "contacto":       datos["contacto"],
        "telefono":       datos["telefono"],
        "correo":         datos["correo"],
    }
    proveedores_mock.append(nuevo_proveedor)
    return nuevo_proveedor

def actualizar_proveedor_en_backend(nit_proveedor: str, datos: dict) -> bool:
    for i, prov in enumerate(proveedores_mock):
        if prov["nit"] == nit_proveedor:
            proveedores_mock[i].update(datos)
            return True
    return False

def eliminar_proveedor_en_backend(nit_proveedor: str) -> bool:
    global proveedores_mock
    longitud_anterior = len(proveedores_mock)
    proveedores_mock[:] = [p for p in proveedores_mock if p["nit"] != nit_proveedor]
    return len(proveedores_mock) < longitud_anterior

# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────
def page(content_container):
    with content_container:
        _loading = LoadingOverlay()
        _loading.build()

        ui.label("Gestión de Proveedores").classes("page-title")
        ui.label("Registro de empresas proveedoras de robots").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        ui.label("Registrar nuevo proveedor").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        # Formulario con validación manual
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_proveedor(form, tabla_proveedores, _loading),
            submit_text="Guardar proveedor",
            enable_validation=True,
            max_length=100,   # límite global para textos
        )
        form.build()

        # Campos del formulario con validaciones
        form.nit = form.add_field(
            "input", "NIT",
            placeholder="900123456",
            required=True,
            max_length=15,
            validation=solo_digitos_nit
        )
        form.nit.props('inputmode=numeric')   # teclado numérico en móviles

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
        "nit":            f.nit.value.strip(),
        "nombre_empresa": f.nombre_empresa.value.strip(),
        "contacto":       (f.contacto.value or "").strip(),
        "telefono":       (f.telefono.value or "").strip(),
        "correo":         (f.correo.value or "").strip(),
    }

    if any(p["nit"] == datos["nit"] for p in proveedores_mock):
        ui.notify(f"Ya existe un proveedor con NIT {datos['nit']}", type="warning")
        return

    def hacer():
        nuevo = registrar_proveedor_en_backend(datos)
        ui.notify(
            f"✅ Proveedor {nuevo['nombre_empresa']} registrado (NIT {nuevo['nit']})",
            type="positive",
        )
        f.nit.value = ""
        f.nombre_empresa.value = ""
        f.contacto.value = ""
        f.telefono.value = ""
        f.correo.value = ""
        f.clear_errors()
        return nuevo

    def refrescar():
        tabla_ref.set_data(proveedores_mock)

    await with_spinner(_loading, hacer, refresh=refrescar)

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
                    "contacto":       (inp_contacto.value or "").strip(),
                    "telefono":       (inp_telefono.value or "").strip(),
                    "correo":         (inp_correo.value or "").strip(),
                }

                def editar():
                    ok = actualizar_proveedor_en_backend(fila["nit"], datos_actualizados)
                    if ok:
                        ui.notify(
                            f"✅ Proveedor {datos_actualizados['nombre_empresa']} actualizado",
                            type="positive",
                        )
                        dialogo.close()
                    else:
                        ui.notify("No se encontró el proveedor para actualizar", type="negative")
                    return ok

                def refrescar():
                    tabla_ref.set_data(proveedores_mock)

                await with_spinner(_loading, editar, refresh=refrescar)

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
                def eliminar():
                    ok = eliminar_proveedor_en_backend(fila["nit"])
                    if ok:
                        ui.notify(
                            f"🗑️ Proveedor {fila['nombre_empresa']} eliminado",
                            type="positive",
                        )
                        dialogo.close()
                    else:
                        ui.notify("No se encontró el proveedor para eliminar", type="negative")
                    return ok

                def refrescar():
                    tabla_ref.set_data(proveedores_mock)

                await with_spinner(_loading, eliminar, refresh=refrescar)

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()