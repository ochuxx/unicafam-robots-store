# FrontEnd/pages/04_empleados.py
from nicegui import ui
from components.forms import SmartForm

def page(content_container):
    with content_container:
        ui.label("Gestión de Empleados").classes("page-title")
        ui.label("Registro de personal").classes("page-subtitle").style("margin-bottom: 24px;")
        
        ui.label("Registrar nuevo empleado").classes("text-h6").style("color: var(--teal-light);")
        
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: registrar_empleado(form),
            submit_text="Guardar empleado"
        )
        form.build()
        
        # Documento de identidad (id_empleado) obligatorio
        documento = form.add_field("input", "Documento de identidad", placeholder="Ej: 12345678", required=True)
        nombre = form.add_field("input", "Nombre completo", placeholder="Nombres y apellidos")
        cargo = form.add_field("input", "Cargo", placeholder="Ej: Vendedor, Técnico, Administrador")
        correo = form.add_field("email", "Correo electrónico", placeholder="empleado@empresa.com")
        telefono = form.add_field("input", "Teléfono", placeholder="300 000 0000")
        
        # Guardar referencias
        form.documento = documento
        form.nombre = nombre
        form.cargo = cargo
        form.correo = correo
        form.telefono = telefono
        
        def registrar_empleado(f):
            if not f.documento.value or not f.nombre.value:
                ui.notify("Documento y nombre son obligatorios", type="negative")
                return
            ui.notify(f"Empleado {f.nombre.value} (Doc: {f.documento.value}) registrado", type="positive")
            # Limpiar campos
            f.documento.value = ""
            f.nombre.value = ""
            f.cargo.value = ""
            f.correo.value = ""
            f.telefono.value = ""
        
        ui.separator().classes("my-6")
        ui.label("Listado de empleados").classes("text-h6").style("color: var(--teal-light);")
        with ui.card().classes("w-full bg-card p-6 rounded-lg"):
            ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
            ui.label("Tabla de empleados en construcción").classes("text-center text-muted")
            ui.label("Próximamente se mostrará el personal registrado.").classes("text-center text-muted text-sm")