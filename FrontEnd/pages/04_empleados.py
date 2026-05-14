from nicegui import ui

def page(content_container):
    with content_container:
        ui.label("Empleados").classes("page-title")
        ui.label("Gestión de personal - En construcción").classes("page-subtitle")
        with ui.card().classes('bg-card border border-teal-accent p-8 rounded-lg'):
            ui.html('<div style="font-size:3rem; text-align:center;">🚧</div>')
            ui.label("Próximamente").classes("text-2xl text-teal-light text-center")