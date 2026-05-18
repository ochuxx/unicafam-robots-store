# FrontEnd/pages/03_proveedores.py
from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import proveedores_mock

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────

def registrar_proveedor_en_backend(datos: dict) -> dict:
    """
    Agrega un nuevo proveedor a la base de datos mock (proveedores_mock).

    :param datos: Diccionario con las claves: nit, nombre_empresa, contacto, telefono, correo.
    :return: El diccionario del proveedor recién creado.
    """
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
    """
    Actualiza los datos de un proveedor existente en proveedores_mock.

    :param nit_proveedor: NIT del proveedor a actualizar.
    :param datos: Diccionario con los campos a actualizar (nombre_empresa, contacto, telefono, correo).
    :return: True si se encontró y actualizó, False en caso contrario.
    """
    for i, prov in enumerate(proveedores_mock):
        if prov["nit"] == nit_proveedor:
            proveedores_mock[i].update(datos)
            return True
    return False


def eliminar_proveedor_en_backend(nit_proveedor: str) -> bool:
    """
    Elimina un proveedor de proveedores_mock por su NIT.

    :param nit_proveedor: NIT del proveedor a eliminar.
    :return: True si se eliminó al menos un proveedor, False si no se encontró.
    """
    global proveedores_mock
    longitud_anterior = len(proveedores_mock)
    proveedores_mock[:] = [p for p in proveedores_mock if p["nit"] != nit_proveedor]
    return len(proveedores_mock) < longitud_anterior


# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────

def page(content_container):
    """
    Renderiza la página de gestión de proveedores en el contenedor proporcionado.

    Incluye:
    - Formulario de registro (SmartForm con 2 columnas).
    - Tabla de proveedores (SmartTable) con acciones editar/eliminar.
    - Diálogos para edición y confirmación de eliminación.

    :param content_container: Contenedor (ui.column) donde se montará la página.
    """
    with content_container:
        ui.label("Gestión de Proveedores").classes("page-title")
        ui.label("Registro de empresas proveedoras de robots").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        # ── Formulario de registro ───────────────────────────────────
        ui.label("Registrar nuevo proveedor").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_proveedor(form, tabla_proveedores),
            submit_text="Guardar proveedor",
        )
        form.build()

        # Campos del formulario
        form.nit           = form.add_field("input", "NIT", placeholder="Ej: 900123456-7", required=True)
        form.nombre_empresa= form.add_field("input", "Nombre empresa", placeholder="Ej: RoboTech S.A.S")
        form.contacto      = form.add_field("input", "Persona de contacto", placeholder="Nombre del representante")
        form.telefono      = form.add_field("input", "Teléfono", placeholder="300 000 0000")
        form.correo        = form.add_field("email", "Correo electrónico", placeholder="contacto@empresa.com")

        ui.separator().classes("my-6")

        # ── Tabla de proveedores ─────────────────────────────────────
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
            on_action=lambda accion, fila: _manejar_accion_proveedor(accion, fila, tabla_proveedores),
            row_key="nit",
            max_height="500px",
            filterable=True,
        )
        tabla_proveedores.build()


# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────

def _registrar_proveedor(f: SmartForm, tabla_ref: SmartTable) -> None:
    """
    Callback del botón Guardar proveedor. Valida el formulario, persiste el proveedor
    y refresca la tabla.

    :param f: Instancia del SmartForm con los campos.
    :param tabla_ref: Referencia a la SmartTable para actualizar los datos.
    """
    if not f.nit.value or not f.nombre_empresa.value:
        ui.notify("NIT y nombre de empresa son obligatorios", type="negative")
        return

    datos = {
        "nit":           f.nit.value.strip(),
        "nombre_empresa": f.nombre_empresa.value.strip(),
        "contacto":      (f.contacto.value or "").strip(),
        "telefono":      (f.telefono.value or "").strip(),
        "correo":        (f.correo.value or "").strip(),
    }

    # Verificar NIT duplicado
    nits_existentes = {p["nit"] for p in proveedores_mock}
    if datos["nit"] in nits_existentes:
        ui.notify(f"Ya existe un proveedor con NIT {datos['nit']}", type="warning")
        return

    nuevo = registrar_proveedor_en_backend(datos)
    ui.notify(
        f"✅ Proveedor {nuevo['nombre_empresa']} registrado (NIT {nuevo['nit']})",
        type="positive",
    )

    # Limpiar formulario
    f.nit.value = ""
    f.nombre_empresa.value = ""
    f.contacto.value = ""
    f.telefono.value = ""
    f.correo.value = ""

    tabla_ref.set_data(proveedores_mock)


def _manejar_accion_proveedor(accion: str, fila: dict, tabla_ref: SmartTable) -> None:
    """
    Despachador de acciones de la tabla de proveedores.

    :param accion: Nombre de la acción ('editar' o 'eliminar').
    :param fila: Diccionario con los datos del proveedor.
    :param tabla_ref: Referencia a la SmartTable para actualizar después de cambios.
    """
    if accion == "editar":
        _abrir_dialogo_edicion_proveedor(fila, tabla_ref)
    elif accion == "eliminar":
        _confirmar_eliminacion_proveedor(fila, tabla_ref)


def _abrir_dialogo_edicion_proveedor(fila: dict, tabla_ref: SmartTable) -> None:
    """
    Abre un diálogo modal con los datos del proveedor para editarlos.

    :param fila: Datos actuales del proveedor.
    :param tabla_ref: Referencia a la tabla para refrescar después de guardar.
    """
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

            def guardar():
                if not inp_nombre_empresa.value:
                    ui.notify("El nombre de la empresa es obligatorio", type="negative")
                    return

                datos_actualizados = {
                    "nombre_empresa": inp_nombre_empresa.value.strip(),
                    "contacto":       (inp_contacto.value or "").strip(),
                    "telefono":       (inp_telefono.value or "").strip(),
                    "correo":         (inp_correo.value or "").strip(),
                }
                ok = actualizar_proveedor_en_backend(fila["nit"], datos_actualizados)
                if ok:
                    ui.notify(
                        f"✅ Proveedor {datos_actualizados['nombre_empresa']} actualizado",
                        type="positive",
                    )
                    tabla_ref.set_data(proveedores_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el proveedor para actualizar", type="negative")

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()


def _confirmar_eliminacion_proveedor(fila: dict, tabla_ref: SmartTable) -> None:
    """
    Abre un diálogo de confirmación antes de eliminar el proveedor.

    :param fila: Datos del proveedor a eliminar.
    :param tabla_ref: Referencia a la tabla para refrescar después de eliminar.
    """
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

            def confirmar():
                ok = eliminar_proveedor_en_backend(fila["nit"])
                if ok:
                    ui.notify(
                        f"🗑️ Proveedor {fila['nombre_empresa']} eliminado",
                        type="positive",
                    )
                    tabla_ref.set_data(proveedores_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el proveedor para eliminar", type="negative")

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()