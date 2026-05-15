# FrontEnd/main.py
import sys
from pathlib import Path
from nicegui import ui
from config.global_styles import apply_global_styles, create_sidebar_layout
from importlib import import_module
import logging

# Agregar el directorio actual al path para poder importar módulos locales
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

logging.basicConfig(level=logging.INFO)

# Mapeo de nombre de sección a nombre del archivo (sin extensión)
SECCIONES = {
    'dashboard': '00_dashboard',
    'clientes': '01_clientes',
    'robots': '02_robots',
    'proveedores': '03_proveedores',
    'empleados': '04_empleados',
    'ventas': '05_ventas',
    'soporte': '06_soporte',
    'consultas': '07_consultas',
    'inventario': '08_inventario',
    'prueba': '99_prueba',
}

def cargar_pagina(section_name: str):
    """Retorna la función 'page' del módulo correspondiente o None si no existe."""
    module_name = SECCIONES.get(section_name)
    if not module_name:
        logging.warning(f"Sección no mapeada: {section_name}")
        return None
    try:
        # Importar desde el paquete 'pages' (mismo nivel que este archivo)
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
        pagina_func = cargar_pagina(section_name)
        if pagina_func:
            pagina_func(content_container)
        else:
            with content_container:
                ui.label(f"Sección '{section_name}' no encontrada").classes("text-red")
    
    create_sidebar_layout(content_container, render_section)
    render_section('dashboard')

ui.run(
    title="SmartBot Solutions — Sistema de Gestión",
    dark=True,
    port=8080,
    favicon="🤖",
    storage_secret="smartbot-2026"
)