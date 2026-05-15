# FrontEnd/pages/05_ventas.py
from nicegui import ui
from components.forms import SmartForm
from datetime import datetime

# ==================================================
# DATOS MOCK
# ==================================================
CLIENTES_MOCK = [
    {"id": 1, "nombre": "Ana Torres"},
    {"id": 2, "nombre": "Luis Martínez"},
    {"id": 3, "nombre": "Sara Gómez"},
]

EMPLEADOS_MOCK = [
    {"id": 1, "nombre": "Carlos Vendedor"},
    {"id": 2, "nombre": "María Soporte"},
]

ROBOTS_MOCK = [
    {"id": 1, "nombre": "HomeBot X1", "precio": 4500000},
    {"id": 2, "nombre": "InduBot Pro", "precio": 18000000},
    {"id": 3, "nombre": "EduBot Kids", "precio": 1200000},
]

# Variables globales simuladas
ultimo_id_venta = 0
contador_detalle = 0
filas_detalle = {}

def generar_id_venta():
    global ultimo_id_venta
    ultimo_id_venta += 1
    return ultimo_id_venta

def generar_id_detalle():
    global contador_detalle
    contador_detalle += 1
    return contador_detalle

def page(content_container):
    with content_container:
        ui.label("Gestión de Ventas").classes("page-title")
        ui.label("Registro de transacciones con detalles").classes("page-subtitle").style("margin-bottom: 24px;")

        # ---------- CABECERA (SmartForm) ----------
        ui.label("Datos de la venta").classes("text-h6").style("color: var(--teal-light); margin-bottom: 8px;")
        form = SmartForm(title="", subtitle="", padding="8px", gap="16px", columns=2, max_width="100%")
        form.build()
        fecha_venta = form.add_field("date", "Fecha de venta", value=datetime.now().strftime("%Y-%m-%d"))
        opciones_cliente = [f"{c['id']} - {c['nombre']}" for c in CLIENTES_MOCK]
        cliente = form.add_field("select", "Cliente", options=opciones_cliente)
        opciones_empleado = [f"{e['id']} - {e['nombre']}" for e in EMPLEADOS_MOCK]
        empleado = form.add_field("select", "Empleado responsable", options=opciones_empleado)
        form.fecha = fecha_venta
        form.cliente = cliente
        form.empleado = empleado

        # ---------- CONTENEDORES PARA DETALLES (se crearán ANTES de las funciones) ----------
        ui.separator().classes("my-4")
        ui.label("Productos vendidos").classes("text-h6").style("color: var(--teal-light); margin-bottom: 8px;")
        detalles_container = ui.column().classes("w-full gap-2")
        total_general_label = ui.label("Total general: $0").classes("text-h6 text-right").style("color: var(--teal-light); margin-top: 16px;")
        
        # ---------- DEFINICIÓN DE FUNCIONES (usando los contenedores creados) ----------
        def actualizar_total_general():
            total = 0
            for data in filas_detalle.values():
                cantidad = data['cantidad'].value or 0
                precio = data['precio']
                total += cantidad * precio
            total_general_label.set_text(f"Total general: ${total:,.0f}")
            print(f"Total actualizado: {total}")  # Depuración

        def actualizar_subtotal(idx):
            data = filas_detalle.get(idx)
            if data:
                cantidad = data['cantidad'].value or 0
                precio = data['precio']
                subtotal = cantidad * precio
                data['subtotal'].set_text(f"${subtotal:,.0f}")
                actualizar_total_general()

        def eliminar_fila(fila_element, idx):
            fila_element.clear()
            if idx in filas_detalle:
                del filas_detalle[idx]
            actualizar_total_general()
            print(f"Fila {idx} eliminada")

        def actualizar_precio_por_robot(idx):
            data = filas_detalle.get(idx)
            if not data:
                return
            seleccion = data['robot'].value
            if seleccion:
                try:
                    id_str = seleccion.split(" - ")[0]
                    robot_id = int(id_str)
                    robot = next((r for r in ROBOTS_MOCK if r['id'] == robot_id), None)
                    if robot:
                        data['precio'] = robot['precio']
                        print(f"Robot {robot_id} seleccionado, precio {robot['precio']}")
                except (ValueError, IndexError):
                    data['precio'] = 0
            else:
                data['precio'] = 0
            actualizar_subtotal(idx)

        def agregar_fila_detalle():
            global filas_detalle
            nuevo_id = generar_id_detalle()
            opciones_robot = [f"{r['id']} - {r['nombre']} (${r['precio']:,.0f})" for r in ROBOTS_MOCK]
            with detalles_container:
                with ui.row().classes("w-full gap-2 items-center").style("margin-bottom: 8px;") as fila:
                    robot_sel = ui.select(
                        options=opciones_robot,
                        label="Robot",
                        value=opciones_robot[0] if opciones_robot else None,
                        on_change=lambda i=nuevo_id: actualizar_precio_por_robot(i)
                    ).classes("flex-1")
                    cantidad_inp = ui.number(value=1, min=1, label="Cantidad", on_change=lambda i=nuevo_id: actualizar_subtotal(i)).classes("w-24")
                    subtotal_lbl = ui.label("$0").classes("w-24 text-right")
                    eliminar_btn = ui.button("🗑️", on_click=lambda i=nuevo_id: eliminar_fila(fila, i)).props("flat").style("color: var(--text-muted);")
                    filas_detalle[nuevo_id] = {
                        'fila': fila,
                        'robot': robot_sel,
                        'cantidad': cantidad_inp,
                        'subtotal': subtotal_lbl,
                        'precio': 0
                    }
                    actualizar_precio_por_robot(nuevo_id)
            actualizar_total_general()
            print(f"Fila agregada, total filas: {len(filas_detalle)}")

        def guardar_venta_completa():
            if not form.cliente.value or not form.empleado.value:
                ui.notify("Debe seleccionar cliente y empleado", type="negative")
                return
            if not filas_detalle:
                ui.notify("Debe agregar al menos un producto", type="negative")
                return
            nuevo_id_venta = generar_id_venta()
            total_venta = 0
            for data in filas_detalle.values():
                cantidad = data['cantidad'].value or 0
                precio = data['precio']
                total_venta += cantidad * precio
            ui.notify(f"Venta #{nuevo_id_venta} registrada con {len(filas_detalle)} productos. Total: ${total_venta:,.0f}", type="positive", position="top")
            print(f"Venta {nuevo_id_venta} guardada")
            # Limpiar
            form.fecha.value = datetime.now().strftime("%Y-%m-%d")
            form.cliente.value = None
            form.empleado.value = None
            for data in list(filas_detalle.values()):
                data['fila'].clear()
            filas_detalle.clear()
            global contador_detalle
            contador_detalle = 0
            actualizar_total_general()

        # ---------- BOTONES (con callbacks directos, después de definir funciones) ----------
        with ui.row().classes("justify-end mt-2"):
            ui.button("➕ Agregar producto", on_click=agregar_fila_detalle).props("flat").style("border: 1px solid var(--teal-mid);")
        with ui.row().classes("justify-end mt-4"):
            ui.button("Registrar venta", on_click=guardar_venta_completa).props("unelevated").style("background: var(--teal-mid); color: white;")

        # ---------- LISTADO EN CONSTRUCCIÓN ----------
        ui.separator().classes("my-6")
        ui.label("Listado de ventas").classes("text-h6").style("color: var(--teal-light); margin-bottom: 12px;")
        ui.html('<div style="font-size:2rem; text-align:center;">🚧</div>')
        ui.label("Tabla de ventas en construcción").classes("text-center text-muted")
        ui.label("Próximamente se mostrará el historial de transacciones.").classes("text-center text-muted text-sm")