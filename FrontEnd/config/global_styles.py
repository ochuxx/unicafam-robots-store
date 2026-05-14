# FrontEnd/config/global_styles.py
from nicegui import ui

def apply_global_styles():
    """Inyecta el CSS global y el JavaScript del toggle en la página."""
    ui.add_head_html("""
    <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
      :root {
        --teal-dark:   #0d2b35;
        --teal-mid:    #0e4d5c;
        --teal-accent: #1aabb8;
        --teal-light:  #4dd9e6;
        --bg-dark:     #060f14;
        --bg-card:     #0a1e28;
        --bg-panel:    #0d2535;
        --text-main:   #d0f0f5;
        --text-muted:  #6b9caa;
        --border:      rgba(26,171,184,0.2);
      }
      body, .nicegui-content {
        background: var(--bg-dark) !important;
        font-family: 'Exo 2', sans-serif !important;
        color: var(--text-main) !important;
        margin: 0; padding: 0;
      }
      ::-webkit-scrollbar { width: 6px; }
      ::-webkit-scrollbar-track { background: var(--bg-dark); }
      ::-webkit-scrollbar-thumb { background: var(--teal-mid); border-radius: 3px; }

      /* Sidebar */
      .sidebar-wrapper {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        z-index: 1000;
        width: 260px;
        background: linear-gradient(180deg, var(--teal-dark) 0%, var(--bg-dark) 100%);
        border-right: 1px solid var(--border);
        box-shadow: 4px 0 24px rgba(0,0,0,0.4);
        display: flex;
        flex-direction: column;
        transition: transform 0.3s ease;
        overflow: hidden;
      }
      .sidebar-wrapper.hidden {
        transform: translateX(-260px);
      }
      .sidebar-scroll {
        flex: 1;
        overflow-y: auto;
        padding: 0 0 20px 0;
      }
      .sidebar-scroll::-webkit-scrollbar { width: 4px; }
      .sidebar-scroll::-webkit-scrollbar-thumb { background: var(--teal-accent); }

      .sidebar-logo {
        padding: 20px 20px 12px;
        border-bottom: 1px solid var(--border);
        text-align: center;
        flex-shrink: 0;
      }
      .sidebar-logo .brand {
        font-size: 1.2rem; font-weight: 800; color: var(--teal-light);
        text-transform: uppercase;
      }
      .sidebar-logo .sub {
        font-size: 0.65rem; color: var(--text-muted); letter-spacing: 3px;
      }
      .nav-section {
        padding: 16px 20px 4px;
        font-size: 0.6rem; color: var(--text-muted);
        letter-spacing: 2.5px; text-transform: uppercase; font-weight: 700;
      }
      .nav-btn {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 20px;
        margin: 2px 12px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.85rem; font-weight: 600;
        color: var(--text-muted);
        transition: all 0.2s;
        border: none; background: transparent;
        width: calc(100% - 24px);
        text-align: left;
      }
      .nav-btn:hover { background: rgba(26,171,184,0.12); color: var(--teal-light); }
      .nav-btn.active {
        background: rgba(26,171,184,0.18);
        color: var(--teal-light);
        border-left: 3px solid var(--teal-accent);
      }
      .sidebar-footer {
        flex-shrink: 0;
        padding: 16px 20px;
        border-top: 1px solid var(--border);
        font-size: 0.65rem; color: var(--text-muted);
        text-align: center;
      }
      .sidebar-footer span { color: var(--teal-accent); }

      /* Toggle fuera del sidebar (siempre visible) */
      .toggle-btn {
        position: fixed;
        top: 16px;
        z-index: 1001;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: var(--text-main);
        font-size: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.4);
        transition: left 0.3s ease;
      }
      .toggle-btn:hover { color: var(--teal-light); transform: scale(1.05); }
      .toggle-btn.right { left: 270px; }
      .toggle-btn.left  { left: 16px; }

      /* Main content */
      .main-content {
        margin-left: 260px;
        padding: 28px 32px 28px 80px;
        min-height: 100vh;
        transition: margin-left 0.3s ease;
      }
      .main-content.expanded {
        margin-left: 0;
        padding-left: 80px;
      }
      .page-title { font-size: 1.6rem; font-weight: 800; color: var(--teal-light); margin: 0; }
      .page-subtitle { color: var(--text-muted); font-size: 0.8rem; margin-top: 4px; }
    </style>
    """, shared=True)

    # JavaScript para el toggle (se inyecta una sola vez)
    ui.add_body_html("""
    <script>
    function toggleSidebar() {
        const wrapper = document.querySelector('.sidebar-wrapper');
        const toggle = document.querySelector('.toggle-btn');
        const mainContent = document.querySelector('.main-content');

        wrapper.classList.toggle('hidden');
        toggle.classList.toggle('right');
        toggle.classList.toggle('left');
        if (mainContent) mainContent.classList.toggle('expanded');
    }
    </script>
    """, shared=True)

def create_sidebar_layout(content_container, render_section):
    """
    Construye el sidebar y el toggle.
    
    Args:
        content_container: ui.column donde se renderizará el contenido.
        render_section: función que recibe (section_name) y renderiza el contenido.
    """
    # Toggle
    with ui.element('div').classes('toggle-btn right') as toggle:
        ui.label('☰')
    toggle.on('click', lambda: ui.run_javascript('toggleSidebar()'))

    # Sidebar
    with ui.element('div').classes('sidebar-wrapper'):
        # Logo
        ui.html('''
        <div class="sidebar-logo">
            <div style="font-size:2rem;margin-bottom:4px">🤖</div>
            <div class="brand">SmartBot</div>
            <div class="sub">Solutions</div>
        </div>
        ''')

        nav_buttons = {}  # Diccionario para manejar el estado activo

        # Función auxiliar para actualizar el botón activo
        def set_active_section(section_name):
            # Quita la clase 'active' de todos los botones
            for btn in nav_buttons.values():
                btn.classes(remove='active')
            # Añade la clase 'active' al botón correspondiente
            if section_name in nav_buttons:
                nav_buttons[section_name].classes(add='active')

        # Wrapper que actualiza el activo y renderiza
        def navigate_to(section_name):
            set_active_section(section_name)
            render_section(section_name)

        with ui.element('div').classes('sidebar-scroll'):
            # Principal
            ui.html('<div class="nav-section">Principal</div>')
            btn_dash = ui.button('📊 Dashboard', on_click=lambda: navigate_to('dashboard')).props('flat').classes('nav-btn active')
            nav_buttons['dashboard'] = btn_dash

            # Datos maestros
            ui.html('<div class="nav-section">Datos maestros</div>')
            btn_clientes = ui.button('👥 Clientes', on_click=lambda: navigate_to('clientes')).props('flat').classes('nav-btn')
            nav_buttons['clientes'] = btn_clientes
            btn_robots = ui.button('🤖 Robots', on_click=lambda: navigate_to('robots')).props('flat').classes('nav-btn')
            nav_buttons['robots'] = btn_robots
            btn_proveedores = ui.button('🏭 Proveedores', on_click=lambda: navigate_to('proveedores')).props('flat').classes('nav-btn')
            nav_buttons['proveedores'] = btn_proveedores
            btn_empleados = ui.button('👔 Empleados', on_click=lambda: navigate_to('empleados')).props('flat').classes('nav-btn')
            nav_buttons['empleados'] = btn_empleados

            # Operaciones
            ui.html('<div class="nav-section">Operaciones</div>')
            btn_ventas = ui.button('💰 Ventas', on_click=lambda: navigate_to('ventas')).props('flat').classes('nav-btn')
            nav_buttons['ventas'] = btn_ventas
            btn_soporte = ui.button('🔧 Soporte Técnico', on_click=lambda: navigate_to('soporte')).props('flat').classes('nav-btn')
            nav_buttons['soporte'] = btn_soporte

            # Análisis
            ui.html('<div class="nav-section">Análisis</div>')
            btn_consultas = ui.button('🔍 Consultas', on_click=lambda: navigate_to('consultas')).props('flat').classes('nav-btn')
            nav_buttons['consultas'] = btn_consultas

            # Sección de pruebas
            ui.html('<div class="nav-section">🧪 Pruebas</div>')
            btn_prueba = ui.button('🧪 Área de Pruebas', on_click=lambda: navigate_to('prueba')).props('flat').classes('nav-btn')
            nav_buttons['prueba'] = btn_prueba

        # Footer
        ui.html('''
        <div class="sidebar-footer">
            Unicafam · Gestor de datos 2026<br>
            <span>v1.0</span>
        </div>
        ''')

    return nav_buttons