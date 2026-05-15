# FrontEnd/pages/08_inventario.py
from nicegui import ui
from components.forms import SmartForm
from datetime import datetime

# Datos mock para selects (en producción vendrían de la BD)
ROBOTS_MOCK = [
    {"id": 1, "nombre": "HomeBot X1"},
    {"id": 2, "nombre": "InduBot Pro"},
    {"id": 3, "nombre": "EduBot Kids"},
]
PROVEEDORES_MOCK = [
    {"id": 1, "nombre": "RoboTech S.A.S"},
    {"id": 2, "nombre": "FutureBots"},
    {"id": 3, "nombre": "NanoBot"},
]

def page(content_container):
    with content_container:
        ui.label("Gestión de Inventario").classes("page-title")
        ui.label("Registro de existencias de robots").classes("page-subtitle").style("margin-bottom: 24px;")
        
        ui.label("Registrar entrada de inventario").classes("text-h6").style("color: var(--teal-light);")
        
        form = SmartForm(
            title="", subtitle="",
            padding="20px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: registrar_inventario(form),
            submit_text="Registrar inventario"
        )
        form.build()
        
        # Código de barras (id_inventario) obligatorio
        codigo_barras = form.add_field("input", "Código de barras", placeholder="Ej: 7501234567890", required=True)
        
        # Select de robot
        opciones_robot = [f"{r['id']} - {r['nombre']}" for r in ROBOTS_MOCK]
        robot = form.add_field("select", "Robot", options=opciones_robot)
        
        # Select de proveedor
        opciones_prov = [f"{p['id']} - {p['nombre']}" for p in PROVEEDORES_MOCK]
        proveedor = form.add_field("select", "Proveedor", options=opciones_prov)
        
        precio = form.add_field("number", "Precio de venta (COP)", placeholder="0", value=0)
        stock = form.add_field("number", "Cantidad en stock", placeholder="0", value=0)
        fecha_registro = form.add_field("date", "Fecha de ingreso", value=datetime.now().strftime("%Y-%m-%d"))
        
        # Guardar referencias
        form.codigo_barras = codigo_barras
        form.robot = robot
        form.proveedor = proveedor
        form.precio = precio
        form.stock = stock
        form.fecha_registro = fecha_registro
        
        def registrar_inventario(f):
            if not f.codigo_barras.value:
                ui.notify("El código de barras es obligatorio", type="negative")
                return
            if not f.robot.value or not f.proveedor.value:
                ui.notify("Debe seleccionar robot y proveedor", type="negative")
                return
            if f.precio.value <= 0 or f.stock.value <= 0:
                ui.notify("Precio y stock deben ser mayores a cero", type="negative")
                return
            
            ui.notify(f"Inventario registrado: {f.robot.value} - Stock: {f.stock.value}", type="positive")
            # Limpiar campos (opcional)
            f.codigo_barras.value = ""
            f.robot.value = None
            f.proveedor.value = None
            f.precio.value = 0
            f.stock.value = 0
            f.fecha_registro.value = datetime.now().strftime("%Y-%m-%d")
        
        ui.separator().classes("my-6")
        ui.label("Listado de inventario").classes("text-h6").style("color: var(--teal-light);")
        with ui.card().classes("w-full bg-card p-6 rounded-lg"):
            ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
            ui.label("Tabla de inventario en construcción").classes("text-center text-muted")
            ui.label("Próximamente se mostrarán las existencias por robot.").classes("text-center text-muted text-sm")