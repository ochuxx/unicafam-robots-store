# FrontEnd/pages/01_clientes.py
from nicegui import ui
from components.forms import SmartForm
from datetime import date

def page(content_container):
    with content_container:
        ui.label("Gestión de Clientes").classes("page-title")
        ui.label("Registro y consulta de compradores").classes("page-subtitle").style("margin-bottom: 24px;")
        
        ui.label("Registrar nuevo cliente").classes("text-h6").style("color: var(--teal-light);")
        
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: registrar_cliente(form),
            submit_text="Guardar cliente"
        )
        form.build()
        nit = form.add_field("input", "NIT", placeholder="Ej: 900123456-7")
        nombre = form.add_field("input", "Nombre completo", placeholder="Ej: Juan García")
        correo = form.add_field("email", "Correo electrónico", placeholder="correo@mail.com")
        telefono = form.add_field("input", "Teléfono", placeholder="300 000 0000")
        direccion = form.add_field("input", "Dirección", placeholder="Calle 10 #5-20, Bogotá")
        fecha = form.add_field("date", "Fecha de registro", value=date.today().isoformat())
        
        # Guardar referencias en el form para usarlas en el callback
        form.nit = nit
        form.nombre = nombre
        form.correo = correo
        form.telefono = telefono
        form.direccion = direccion
        form.fecha = fecha
        
        def registrar_cliente(f):
            if not f.nit.value or not f.nombre.value or not f.correo.value:
                ui.notify("NIT, Nombre y Correo son obligatorios", type="negative")
                return
            ui.notify(f"Cliente {f.nombre.value} registrado", type="positive")
            # Limpiar
            f.nit.value = ""
            f.nombre.value = ""
            f.correo.value = ""
            f.telefono.value = ""
            f.direccion.value = ""
            f.fecha.value = date.today().isoformat()
        
        ui.separator().classes("my-6")
        ui.label("Listado de clientes").classes("text-h6").style("color: var(--teal-light);")
        with ui.card().classes("w-full bg-card p-6 rounded-lg"):
            ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
            ui.label("Tabla de clientes en construcción").classes("text-center text-muted")