# FrontEnd/main.py
import sys
from pathlib import Path
from nicegui import ui
from config.global_styles import apply_global_styles, create_sidebar_layout
from importlib import import_module
import logging

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

logging.basicConfig(level=logging.INFO)

SECCIONES = {
    'monitoreo': '00_monitoreo',
    'clientes': '01_clientes',
    'robots': '02_robots',
    'proveedores': '03_proveedores',
    'empleados': '04_empleados',
    'inventario': '05_inventario',
    'ventas': '06_ventas',
    'soporte': '07_soporte',
    'analitica': '08_analitica',
}

def cargar_pagina(section_name: str):
    module_name = SECCIONES.get(section_name)
    if not module_name:
        logging.warning(f"Sección no mapeada: {section_name}")
        return None
    try:
        modulo = import_module(f"pages.{module_name}")
        return getattr(modulo, 'page', None)
    except ImportError as e:
        logging.error(f"Error importando {module_name}: {e}")
        return None

@ui.page("/")
def main():
    apply_global_styles()
    content_container = ui.column().classes("main-content")

    def render_section(section_name: str):
        content_container.clear()
        
        # 1. Mostrar el spinner
        with content_container:
            ui.spinner('dots', size='xl', color='teal').classes('q-mt-xl')
            ui.label('Cargando sección...').classes('text-teal-4 q-mt-md')

        # 2. EL TRUCO: Usamos un timer de 0.1 segundos.
        # Esto le da tiempo al navegador para renderizar el spinner ANTES
        # de que Python comience a procesar la carga pesada de la página.
        def cargar_contenido():
            content_container.clear()
            pagina_func = cargar_pagina(section_name)
            if pagina_func:
                pagina_func(content_container)
            else:
                with content_container:
                    ui.label(f"Sección '{section_name}' no encontrada").classes("text-red")
            timer.deactivate() # Detenemos el timer para que no se ejecute más veces

        timer = ui.timer(0.1, cargar_contenido, once=True)

    create_sidebar_layout(render_section)
    render_section('monitoreo')

ui.run(
    title="SmartBot Solutions — Sistema de Gestión",
    dark=True,
    port=8080,
    favicon="🤖",
    storage_secret="smartbot-2026"
)