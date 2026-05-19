from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from datetime import date
from mock_data import clientes_mock
import re

def solo_digitos(valor):
    """Valida que el NIT contenga solo dígitos."""
    if not valor:
        return True  # El required se encarga del vacío
    if not re.match(r'^\d+$', valor):
        return "El NIT solo puede contener números (sin puntos, guiones ni espacios)"
    return True

def registrar_cliente_en_backend(datos: dict) -> dict:
    nuevo_cliente = {
        "nit": datos["nit"],
        "nombre": datos["nombre"],
        "correo": datos["correo"],
        "telefono": datos["telefono"],
        "direccion": datos["direccion"],
        "fecha_registro": datos["fecha_registro"],
    }
    clientes_mock.append(nuevo_cliente)
    return nuevo_cliente

def actualizar_cliente_en_backend(nit_cliente: str, datos: dict) -> bool:
    for i, cliente in enumerate(clientes_mock):
        if cliente["nit"] == nit_cliente:
            clientes_mock[i].update(datos)
            return True
    return False

def eliminar_cliente_en_backend(nit_cliente: str) -> bool:
    global clientes_mock
    longitud_anterior = len(clientes_mock)
    clientes_mock[:] = [c for c in clientes_mock if c["nit"] != nit_cliente]
    return len(clientes_mock) < longitud_anterior

def page(content_container):
    with content_container:
        ui.label("Gestión de Clientes").classes("page-title")
        ui.label("Registro y consulta de compradores").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        ui.label("Registrar nuevo cliente").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        # Formulario
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar_cliente(form, tabla_clientes),
            submit_text="Guardar cliente",
            enable_validation=True,
            max_length=100,
        )
        form.build()

        # Campos (orden correcto)
        form.nit = form.add_field(
            "input", "NIT",
            placeholder="900123456",
            required=True,
            max_length=10,
            validation=solo_digitos
        )
        form.nit.props('inputmode=numeric')   # Teclado numérico en móviles

        form.nombre = form.add_field(
            "input", "Nombre completo",
            placeholder="Ej: Juan García",
            required=True,
            max_length=80
        )
        form.correo = form.add_field(
            "email", "Correo electrónico",
            placeholder="correo@mail.com",
            required=True,
            max_length=100
        )
        form.telefono = form.add_field(
            "input", "Teléfono",
            placeholder="300 000 0000"
        )
        form.direccion = form.add_field(
            "input", "Dirección",
            placeholder="Calle 10 #5-20, Bogotá"
        )
        form.fecha = form.add_field(
            "date", "Fecha de registro",
            value=date.today().isoformat()
        )

        ui.separator().classes("my-6")

        ui.label("Listado de clientes").classes("text-h6").style(
            "color: var(--teal-light);"
        )

        columnas_clientes = [
            {"label": "NIT", "field": "nit", "width": "150px", "filter_mode": "exact"},
            {"label": "Nombre", "field": "nombre", "width": "180px", "filter_mode": "exact"},
            {"label": "Correo", "field": "correo", "width": "190px", "filter_mode": "contains"},
            {"label": "Teléfono", "field": "telefono", "width": "130px", "filter_mode": "contains"},
            {"label": "Dirección", "field": "direccion", "width": "180px", "filter_mode": "contains"},
            {"label": "Fecha Registro", "field": "fecha_registro", "width": "120px", "filter_mode": "startswith"},
        ]

        acciones = {
            "editar": {"icon": "edit", "color": "amber", "tooltip": "Editar cliente"},
            "eliminar": {"icon": "delete", "color": "red", "tooltip": "Eliminar cliente"},
        }

        tabla_clientes = SmartTable(
            columns=columnas_clientes,
            data=clientes_mock,
            title="",
            subtitle="",
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion(accion, fila, tabla_clientes),
            row_key="nit",
            max_height="500px",
            filterable=True,
        )
        tabla_clientes.build()

def _registrar_cliente(f: SmartForm, tabla_ref: SmartTable) -> None:
    # Validar todos los campos del formulario
    if not f.is_valid():
        ui.notify("Corrige los errores marcados en el formulario", type="warning")
        return

    # Datos del formulario (el NIT ya es string)
    datos = {
        "nit": f.nit.value.strip(),
        "nombre": f.nombre.value.strip(),
        "correo": f.correo.value.strip(),
        "telefono": (f.telefono.value or "").strip(),
        "direccion": (f.direccion.value or "").strip(),
        "fecha_registro": f.fecha.value,
    }

    # Validación de negocio: NIT duplicado
    if any(c["nit"] == datos["nit"] for c in clientes_mock):
        ui.notify(f"Ya existe un cliente con NIT {datos['nit']}", type="warning")
        return

    nuevo = registrar_cliente_en_backend(datos)
    ui.notify(f"✅ Cliente {nuevo['nombre']} registrado (NIT {nuevo['nit']})", type="positive")

    # Limpiar formulario
    f.nit.value = ""
    f.nombre.value = ""
    f.correo.value = ""
    f.telefono.value = ""
    f.direccion.value = ""
    f.fecha.value = date.today().isoformat()
    f.clear_errors()

    tabla_ref.set_data(clientes_mock)

def _manejar_accion(accion: str, fila: dict, tabla_ref: SmartTable) -> None:
    if accion == "editar":
        _abrir_dialogo_edicion(fila, tabla_ref)
    elif accion == "eliminar":
        _confirmar_eliminacion(fila, tabla_ref)

def _abrir_dialogo_edicion(fila: dict, tabla_ref: SmartTable) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 480px; padding: 24px;"):
        ui.label(f"Editar cliente — {fila['nit']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 16px;"
        )

        inp_nombre = ui.input("Nombre completo", value=fila.get("nombre", "")).classes("w-full")
        inp_correo = ui.input("Correo electrónico", value=fila.get("correo", "")).classes("w-full")
        inp_telefono = ui.input("Teléfono", value=fila.get("telefono", "")).classes("w-full")
        inp_direccion = ui.input("Dirección", value=fila.get("direccion", "")).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def guardar():
                if not inp_nombre.value or not inp_correo.value:
                    ui.notify("Nombre y Correo son obligatorios", type="negative")
                    return

                datos_actualizados = {
                    "nombre": inp_nombre.value.strip(),
                    "correo": inp_correo.value.strip(),
                    "telefono": (inp_telefono.value or "").strip(),
                    "direccion": (inp_direccion.value or "").strip(),
                }
                ok = actualizar_cliente_en_backend(fila["nit"], datos_actualizados)
                if ok:
                    ui.notify(f"✅ Cliente {datos_actualizados['nombre']} actualizado", type="positive")
                    tabla_ref.set_data(clientes_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el cliente para actualizar", type="negative")

            ui.button("Guardar cambios", on_click=guardar).props("unelevated color=teal")

    dialogo.open()

def _confirmar_eliminacion(fila: dict, tabla_ref: SmartTable) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar cliente").classes("text-h6").style("color: #F44336; margin-bottom: 8px;")
        ui.label(
            f"¿Estás seguro de que deseas eliminar a {fila['nombre']} "
            f"(NIT {fila['nit']})? Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def confirmar():
                ok = eliminar_cliente_en_backend(fila["nit"])
                if ok:
                    ui.notify(f"🗑️ Cliente {fila['nombre']} eliminado", type="positive")
                    tabla_ref.set_data(clientes_mock)
                    dialogo.close()
                else:
                    ui.notify("No se encontró el cliente para eliminar", type="negative")

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()