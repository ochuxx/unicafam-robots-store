# FrontEnd/pages/06_soporte.py
from nicegui import ui
from components.forms import SmartForm
from components.table import SmartTable
from mock_data import clientes_mock, robots_mock, soporte_mock
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────────────

ESTADOS_TICKET = ["Abierto", "En progreso", "Resuelto", "Cerrado"]

OPCIONES_CLIENTE = [f"{c['nit']} - {c['nombre']}" for c in clientes_mock]
OPCIONES_ROBOT   = [f"{r['id']} - {r['nombre']}"  for r in robots_mock]

# ──────────────────────────────────────────────────────────────────────
# Operaciones de backend (mock)
# ──────────────────────────────────────────────────────────────────────

def _siguiente_id() -> int:
    return max((t["id"] for t in soporte_mock), default=0) + 1


def registrar_ticket(datos: dict) -> dict:
    nuevo = {
        "id":            _siguiente_id(),
        "fecha_reporte": datos["fecha_reporte"],
        "problema":      datos["problema"],
        "estado":        "Abierto",
        "id_cliente":    datos["id_cliente"],
        "id_robot":      datos["id_robot"],
    }
    soporte_mock.append(nuevo)
    return nuevo


def actualizar_estado(id_ticket: int, nuevo_estado: str) -> bool:
    for ticket in soporte_mock:
        if ticket["id"] == id_ticket:
            ticket["estado"] = nuevo_estado
            return True
    return False


def eliminar_ticket(id_ticket: int) -> bool:
    longitud_anterior = len(soporte_mock)
    soporte_mock[:] = [t for t in soporte_mock if t["id"] != id_ticket]
    return len(soporte_mock) < longitud_anterior


# ──────────────────────────────────────────────────────────────────────
# Helpers de visualización
# ──────────────────────────────────────────────────────────────────────

def _nombre_cliente(nit: str) -> str:
    c = next((c for c in clientes_mock if c["nit"] == nit), None)
    return f"{nit} - {c['nombre']}" if c else nit


def _nombre_robot(id_robot: str) -> str:
    r = next((r for r in robots_mock if r["id"] == id_robot), None)
    return f"{id_robot} - {r['nombre']}" if r else id_robot


def _construir_filas() -> list:
    return [
        {
            "id":            t["id"],
            "fecha_reporte": t["fecha_reporte"],
            "cliente":       _nombre_cliente(t["id_cliente"]),
            "robot":         _nombre_robot(t["id_robot"]),
            "problema":      t["problema"],
            "estado":        t["estado"],
            "_id_cliente":   t["id_cliente"],
            "_id_robot":     t["id_robot"],
        }
        for t in soporte_mock
    ]


# ──────────────────────────────────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────────────────────────────────

def page(content_container):
    with content_container:
        ui.label("Gestión de Soporte Técnico").classes("page-title")
        ui.label("Registro y seguimiento de solicitudes").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        # ── Formulario de registro ───────────────────────────────────
        ui.label("Nueva solicitud de soporte").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 8px;"
        )

        form = SmartForm(
            title="", subtitle="",
            padding="16px", gap="16px", columns=2, max_width="800px",
            submit_callback=lambda: _registrar(form, tabla),
            submit_text="Registrar solicitud",
        )
        form.build()

        form.fecha    = form.add_field("date", "Fecha del reporte",
                                       value=datetime.now().strftime("%Y-%m-%d"))

        # ui.select con búsqueda habilitada mediante props de Quasar:
        #   use-input      → activa el input de texto dentro del select
        #   input-debounce → espera N ms antes de filtrar (evita lag con 200 opciones)
        #   fill-input     → el texto escrito rellena visualmente el campo
        #   hide-selected  → oculta la opción ya elegida del listado desplegado
        form.cliente = form.add_field("select", "Cliente", options=OPCIONES_CLIENTE)
        form.cliente.props("use-input input-debounce=300 fill-input hide-selected")

        form.robot = form.add_field("select", "Robot", options=OPCIONES_ROBOT)
        form.robot.props("use-input input-debounce=300 fill-input hide-selected")

        form.problema = form.add_field("textarea", "Problema reportado", rows=4,
                                       placeholder="Describa la falla o inconveniente...")

        ui.separator().classes("my-6")

        # ── Tabla de tickets ─────────────────────────────────────────
        ui.label("Listado de solicitudes").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 12px;"
        )

        columnas = [
            {"label": "ID",       "field": "id",            "width": "60px",  "filter_mode": "exact"},
            {"label": "Fecha",    "field": "fecha_reporte", "width": "160px", "filter_mode": "startswith"},
            {"label": "Cliente",  "field": "cliente",       "width": "200px", "filter_mode": "contains"},
            {"label": "Robot",    "field": "robot",         "width": "180px", "filter_mode": "contains"},
            {"label": "Problema", "field": "problema",      "width": "260px", "filter_mode": "contains"},
            {"label": "Estado",   "field": "estado",        "width": "120px", "filter_mode": "exact"},
        ]

        acciones = {
            "cambiar_estado": {"icon": "sync",   "color": "teal", "tooltip": "Cambiar estado"},
            "eliminar":       {"icon": "delete", "color": "red",  "tooltip": "Eliminar ticket"},
        }

        tabla = SmartTable(
            columns=columnas,
            data=_construir_filas(),
            rows_per_page=10,
            show_pagination=True,
            show_actions=True,
            action_buttons=acciones,
            on_action=lambda accion, fila: _manejar_accion(accion, fila, tabla),
            row_key="id",
            max_height="500px",
            filterable=True,
        )
        tabla.build()


# ──────────────────────────────────────────────────────────────────────
# Callbacks internos
# ──────────────────────────────────────────────────────────────────────

def _registrar(f: SmartForm, tabla_ref: SmartTable) -> None:
    if not f.cliente.value or not f.robot.value or not f.problema.value:
        ui.notify("Cliente, robot y problema son obligatorios", type="negative")
        return

    nit_cliente = f.cliente.value.split(" - ")[0].strip()
    id_robot    = f.robot.value.split(" - ")[0].strip()

    nuevo = registrar_ticket({
        "fecha_reporte": f.fecha.value,
        "problema":      f.problema.value.strip(),
        "id_cliente":    nit_cliente,
        "id_robot":      id_robot,
    })

    ui.notify(
        f"✅ Solicitud #{nuevo['id']} registrada — Estado: Abierto",
        type="positive", position="top",
    )

    f.fecha.value    = datetime.now().strftime("%Y-%m-%d")
    f.cliente.value  = None
    f.robot.value    = None
    f.problema.value = ""

    tabla_ref.set_data(_construir_filas())


def _manejar_accion(accion: str, fila: dict, tabla_ref: SmartTable) -> None:
    if accion == "cambiar_estado":
        _dialogo_cambiar_estado(fila, tabla_ref)
    elif accion == "eliminar":
        _dialogo_eliminar(fila, tabla_ref)


def _dialogo_cambiar_estado(fila: dict, tabla_ref: SmartTable) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 420px; padding: 24px;"):
        ui.label(f"Cambiar estado — Ticket #{fila['id']}").classes("text-h6").style(
            "color: var(--teal-light); margin-bottom: 4px;"
        )
        ui.label(f"Problema: {fila['problema']}").style(
            "color: var(--text-muted); font-size: 0.85rem; margin-bottom: 16px;"
        )

        estado_actual = fila["estado"] if fila["estado"] in ESTADOS_TICKET else ESTADOS_TICKET[0]

        sel_estado = ui.select(
            options=ESTADOS_TICKET,
            label="Nuevo estado",
            value=estado_actual,
        ).classes("w-full")

        with ui.row().classes("gap-2 mt-4 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def guardar():
                if not sel_estado.value:
                    ui.notify("Selecciona un estado", type="negative")
                    return
                ok = actualizar_estado(fila["id"], sel_estado.value)
                if ok:
                    ui.notify(
                        f"✅ Ticket #{fila['id']} → {sel_estado.value}",
                        type="positive",
                    )
                    tabla_ref.set_data(_construir_filas())
                    dialogo.close()
                else:
                    ui.notify("No se encontró el ticket", type="negative")

            ui.button("Guardar cambio", on_click=guardar).props("unelevated color=teal")

    dialogo.open()


def _dialogo_eliminar(fila: dict, tabla_ref: SmartTable) -> None:
    with ui.dialog() as dialogo, ui.card().style("min-width: 360px; padding: 24px;"):
        ui.label("Eliminar ticket").classes("text-h6").style(
            "color: #F44336; margin-bottom: 8px;"
        )
        ui.label(
            f"¿Deseas eliminar el ticket #{fila['id']} de {fila['cliente']}? "
            "Esta acción no se puede deshacer."
        ).style("color: var(--text-main); margin-bottom: 16px;")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def confirmar():
                ok = eliminar_ticket(fila["id"])
                if ok:
                    ui.notify(f"🗑️ Ticket #{fila['id']} eliminado", type="positive")
                    tabla_ref.set_data(_construir_filas())
                    dialogo.close()
                else:
                    ui.notify("No se encontró el ticket", type="negative")

            ui.button("Sí, eliminar", on_click=confirmar).props("unelevated color=red")

    dialogo.open()