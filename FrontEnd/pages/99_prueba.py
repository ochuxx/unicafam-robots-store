# FrontEnd/pages/99_prueba.py
from nicegui import ui
from components.forms import SmartForm
from datetime import date

def page(content_container):
    with content_container:
        ui.label("Área de Pruebas").classes("page-title")
        ui.label("Espacio para experimentar con formularios y componentes").classes("page-subtitle").style("margin-bottom: 24px;")
        
        # Aquí puedes colocar el formulario de clientes o cualquier prueba
        ui.label("Formulario de Clientes (Prueba)").classes("text-h6").style("color: var(--teal-light);")
        
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: ui.notify("Prueba guardada", type="positive"),
            submit_text="Guardar"
        )
        form.build()
        form.add_field("input", "NIT", placeholder="900123456-7")
        form.add_field("input", "Nombre", placeholder="Juan García")
        form.add_field("email", "Correo", placeholder="correo@mail.com")
        form.add_field("input", "Teléfono", placeholder="300 000 0000")
        form.add_field("input", "Dirección", placeholder="Calle 10 #5-20")
        form.add_field("date", "Fecha registro", value=date.today().isoformat())