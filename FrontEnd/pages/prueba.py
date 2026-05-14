from nicegui import ui
from components.forms import SmartForm

def prueba_page():
    ui.label("Área de Pruebas").classes("page-title")
    ui.label("Espacio para experimentar con formularios y componentes antes de integrarlos a las páginas definitivas.") \
      .classes("page-subtitle").style("margin-bottom: 24px;")
    
    # Formulario compacto principal
    form = SmartForm(
        title="Nuevo Producto de Prueba",
        subtitle="Campos con espaciado reducido",
        padding="16px",
        gap="12px",
        columns=2,
        max_width="800px",
        submit_callback=lambda: ui.notify("Producto guardado", type="positive"),
        submit_text="Guardar",
        cancel_callback=lambda: ui.notify("Cancelado", type="warning")
    )
    form.build()
    form.add_field("input", "Nombre", placeholder="Nombre del producto")
    form.add_field("number", "Precio", placeholder="0")
    form.add_field("input", "Categoría", placeholder="Ej: Electrónica")
    form.add_field("select", "Estado", options=["Activo", "Inactivo", "En prueba"])
    
    # (Opcional) puedes agregar un textarea de ejemplo si quieres probar el fix
    ui.separator().classes("my-6").style("background: var(--border)")
    ui.label("Prueba de textarea").classes("text-h6").style("color: var(--teal-light);")
    form2 = SmartForm(padding="12px", gap="8px", columns=1, max_width="500px")
    form2.build()
    form2.add_field("textarea", "Comentarios", rows=4, placeholder="Escribe aquí...")