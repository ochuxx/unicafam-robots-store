# FrontEnd/pages/02_robots.py
from nicegui import ui
from components.forms import SmartForm

def page(content_container):
    with content_container:
        ui.label("Gestión de Robots").classes("page-title")
        ui.label("Registro y catálogo de robots").classes("page-subtitle").style("margin-bottom: 24px;")
        
        ui.label("Registrar nuevo robot").classes("text-h6").style("color: var(--teal-light);")
        
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: registrar_robot(form),
            submit_text="Guardar robot"
        )
        form.build()
        
        # Campos del formulario
        id_robot = form.add_field("input", "Número de serie", placeholder="Ej: RB-2024-001", required=True)
        nombre = form.add_field("input", "Nombre del robot", placeholder="Ej: HomeBot X2")
        descripcion = form.add_field("textarea", "Descripción", rows=3, placeholder="Funcionalidades y características")
        tipo = form.add_field("select", "Tipo", options=["Doméstico", "Industrial", "Educativo", "Médico", "Comercial"])
        
        # Guardar referencias
        form.id_robot = id_robot
        form.nombre = nombre
        form.descripcion = descripcion
        form.tipo = tipo
        
        def registrar_robot(f):
            # Validar que número de serie, nombre y tipo no estén vacíos
            if not f.id_robot.value or not f.nombre.value or not f.tipo.value:
                ui.notify("Número de serie, nombre y tipo son obligatorios", type="negative")
                return
            ui.notify(f"Robot '{f.nombre.value}' (Serie: {f.id_robot.value}) registrado", type="positive")
            # Limpiar campos
            f.id_robot.value = ""
            f.nombre.value = ""
            f.descripcion.value = ""
            f.tipo.value = ""
        
        ui.separator().classes("my-6")
        ui.label("Listado de robots").classes("text-h6").style("color: var(--teal-light);")
        with ui.card().classes("w-full bg-card p-6 rounded-lg"):
            ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
            ui.label("Tabla de robots en construcción").classes("text-center text-muted")
            ui.label("Próximamente se mostrará el catálogo completo.").classes("text-center text-muted text-sm")