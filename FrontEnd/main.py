# FrontEnd/main.py
from nicegui import ui
from config.global_styles import apply_global_styles, create_sidebar_layout
from pages.prueba import prueba_page  # Importa la página de pruebas


# ─────────────────────────────────────────────
#  FUNCIÓN DE RENDERIZADO GENÉRICO ("En construcción")
# ─────────────────────────────────────────────
def render_generic(content_container, section_name: str):
    """Renderiza un mensaje 'En construcción' para cualquier sección."""
    content_container.clear()
    with content_container:
        ui.html(f'<div class="page-header"><p class="page-title">{section_name.capitalize()}</p><p class="page-subtitle">Contenido de la sección</p></div>')
        with ui.card().classes('bg-card border border-teal-accent p-8 rounded-lg'):
            ui.html('<div style="font-size:3rem; text-align:center; margin-bottom:16px;">🚧</div>')
            ui.label('En construcción').classes('text-3xl font-bold text-teal-light text-center')
            ui.label('Esta sección estará disponible próximamente.').classes('text-muted text-center mt-2')


# ─────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────
@ui.page("/")
def main():
    # Aplicar estilos y JavaScript globales
    apply_global_styles()

    # Contenedor de contenido
    content_container = ui.column().classes("main-content")

    # Función que el sidebar llamará al hacer clic en un botón
    def render_section(section_name: str):
        # Si es la sección de pruebas, mostramos la página real
        if section_name == 'prueba':
            content_container.clear()
            with content_container:
                prueba_page()
        else:
            # Para el resto, mensaje genérico
            render_generic(content_container, section_name)

    # Crear el sidebar (y el toggle) - ya incluye el botón de 'prueba'
    create_sidebar_layout(content_container, render_section)

    # Renderizar la sección inicial (Dashboard)
    render_section('dashboard')


# ─────────────────────────────────────────────
#  EJECUCIÓN
# ─────────────────────────────────────────────
ui.run(
    title="SmartBot Solutions — Sistema de Gestión",
    dark=True,
    port=8080,
    favicon="🤖",
    storage_secret="smartbot-2026"
)