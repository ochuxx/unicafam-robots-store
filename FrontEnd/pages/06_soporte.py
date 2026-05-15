# FrontEnd/pages/06_soporte.py
from nicegui import ui
from components.forms import SmartForm
from datetime import datetime

# ==================================================
# DATOS MOCK (en producción se obtienen de las tablas Clientes y Robots)
# ==================================================
CLIENTES_MOCK = [
    {"id": 1, "nombre": "Ana Torres"},
    {"id": 2, "nombre": "Luis Martínez"},
    {"id": 3, "nombre": "Sara Gómez"},
]

ROBOTS_MOCK = [
    {"id": 1, "nombre": "HomeBot X1"},
    {"id": 2, "nombre": "InduBot Pro"},
    {"id": 3, "nombre": "EduBot Kids"},
]

# ==================================================
# VARIABLES GLOBALES SIMULADAS
# ==================================================
ultimo_id_soporte = 0

def generar_id_soporte():
    global ultimo_id_soporte
    ultimo_id_soporte += 1
    return ultimo_id_soporte

# ==================================================
# FUNCIÓN PRINCIPAL DE LA PÁGINA
# ==================================================
def page(content_container):
    with content_container:
        ui.label("Gestión de Soporte Técnico").classes("page-title")
        ui.label("Registro y seguimiento de solicitudes").classes("page-subtitle").style("margin-bottom: 24px;")

        # ---------- FORMULARIO DE SOPORTE ----------
        ui.label("Nueva solicitud de soporte").classes("text-h6").style("color: var(--teal-light); margin-bottom: 8px;")
        form = SmartForm(
            title="", subtitle="",
            padding="16px", gap="16px", columns=2, max_width="800px",
            submit_callback=None,
            submit_text="",
            cancel_callback=None
        )
        form.build()

        # Campos del formulario (sin estado)
        fecha_reporte = form.add_field("date", "Fecha del reporte", value=datetime.now().strftime("%Y-%m-%d"))

        opciones_cliente = [f"{c['id']} - {c['nombre']}" for c in CLIENTES_MOCK]
        cliente = form.add_field("select", "Cliente", options=opciones_cliente)

        opciones_robot = [f"{r['id']} - {r['nombre']}" for r in ROBOTS_MOCK]
        robot = form.add_field("select", "Robot", options=opciones_robot)

        problema = form.add_field("textarea", "Problema reportado", rows=4, placeholder="Describa la falla o inconveniente...")

        # Guardar referencias
        form.fecha = fecha_reporte
        form.cliente = cliente
        form.robot = robot
        form.problema = problema

        # Botón guardar
        with ui.row().classes("justify-end mt-2"):
            ui.button("Registrar solicitud", on_click=lambda: guardar_soporte(form)).props("unelevated").style("background: var(--teal-mid); color: white;")

        # ---------- LISTADO EN CONSTRUCCIÓN ----------
        ui.separator().classes("my-6")
        ui.label("Listado de solicitudes").classes("text-h6").style("color: var(--teal-light); margin-bottom: 12px;")
        ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
        ui.label("Tabla de soporte técnico en construcción").classes("text-center text-muted")
        ui.label("Próximamente se mostrará el historial de solicitudes.").classes("text-center text-muted text-sm")

        # ---------- FUNCIÓN DE GUARDADO ----------
        def guardar_soporte(f):
            if not f.cliente.value or not f.robot.value or not f.problema.value:
                ui.notify("Cliente, robot y problema son obligatorios", type="negative")
                return
            nuevo_id = generar_id_soporte()
            # Estado fijo "Abierto" (no se muestra en el formulario)
            estado = "Abierto"
            ui.notify(f"Solicitud #{nuevo_id} registrada. Cliente: {f.cliente.value}, Robot: {f.robot.value}, Estado: {estado}", type="positive", position="top")
            # Limpiar campos
            f.fecha.value = datetime.now().strftime("%Y-%m-%d")
            f.cliente.value = None
            f.robot.value = None
            f.problema.value = ""