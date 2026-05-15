# FrontEnd/pages/03_proveedores.py
from nicegui import ui
from components.forms import SmartForm

def page(content_container):
    with content_container:
        ui.label("Gestión de Proveedores").classes("page-title")
        ui.label("Registro de empresas proveedoras de robots").classes("page-subtitle").style("margin-bottom: 24px;")
        
        ui.label("Registrar nuevo proveedor").classes("text-h6").style("color: var(--teal-light);")
        
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: registrar_proveedor(form),
            submit_text="Guardar proveedor"
        )
        form.build()
        
        # Campos según la tabla Proveedores (NIT = id_proveedor, obligatorio)
        nit = form.add_field("input", "NIT", placeholder="Ej: 900123456-7", required=True)
        nombre_empresa = form.add_field("input", "Nombre empresa", placeholder="Ej: RoboTech S.A.S")
        contacto = form.add_field("input", "Persona de contacto", placeholder="Nombre del representante")
        telefono = form.add_field("input", "Teléfono", placeholder="300 000 0000")
        correo = form.add_field("email", "Correo electrónico", placeholder="contacto@empresa.com")
        
        # Guardar referencias
        form.nit = nit
        form.nombre_empresa = nombre_empresa
        form.contacto = contacto
        form.telefono = telefono
        form.correo = correo
        
        def registrar_proveedor(f):
            if not f.nit.value or not f.nombre_empresa.value:
                ui.notify("NIT y nombre de empresa son obligatorios", type="negative")
                return
            ui.notify(f"Proveedor '{f.nombre_empresa.value}' (NIT: {f.nit.value}) registrado", type="positive")
            # Limpiar campos
            f.nit.value = ""
            f.nombre_empresa.value = ""
            f.contacto.value = ""
            f.telefono.value = ""
            f.correo.value = ""
        
        ui.separator().classes("my-6")
        ui.label("Listado de proveedores").classes("text-h6").style("color: var(--teal-light);")
        with ui.card().classes("w-full bg-card p-6 rounded-lg"):
            ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
            ui.label("Tabla de proveedores en construcción").classes("text-center text-muted")
            ui.label("Próximamente se mostrará el listado de empresas.").classes("text-center text-muted text-sm")