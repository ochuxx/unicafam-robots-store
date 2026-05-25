from nicegui import ui
from mock_data import get_all_mock_data, clientes_mock, robots_mock, inventario_mock, ventas_mock, soporte_mock, detalle_ventas_mock
from dotenv import load_dotenv
import os
import requests
import json
import asyncio

load_dotenv()
GAS_URL = os.getenv("GAS_URL", "").strip()


def format_number_abbreviated(num: float) -> str:
    if num < 1000:
        return f'{num:.0f}'
    elif num < 1_000_000:
        return f'{num / 1_000:.1f}K'
    elif num < 1_000_000_000:
        return f'{num / 1_000_000:.1f}M'
    elif num < 1_000_000_000_000:
        return f'{num / 1_000_000_000:.1f}B'
    else:
        return f'{num / 1_000_000_000_000:.1f}T'


# ----------------------------------------------------------------------
# Funciones de fetch desde GAS
# ----------------------------------------------------------------------
def _fetch_data(action: str, target_list: list, limit: int = 500) -> list:
    if not GAS_URL:
        return []
    payload = {"action": action, "n": limit}
    response = requests.post(GAS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(data.get("message", f"Error al obtener {action}"))
    data_list = data.get("data", [])
    if data_list:
        target_list[:] = data_list
    return data_list


async def _cargar_datos_desde_gas() -> None:
    if not GAS_URL:
        return
    try:
        await asyncio.gather(
            asyncio.to_thread(_fetch_data, "get_clientes", clientes_mock),
            asyncio.to_thread(_fetch_data, "get_robots", robots_mock),
            asyncio.to_thread(_fetch_data, "get_inventarios", inventario_mock),
            asyncio.to_thread(_fetch_data, "get_ventas", ventas_mock),
            asyncio.to_thread(_fetch_data, "get_soportes_tecnicos", soporte_mock),
        )
    except Exception:
        pass


def page(container: ui.column):
    with container:
        ui.label("Monitoreo en Vivo").classes("page-title")
        ui.label("Alertas y última actividad del sistema").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        cards_container = ui.row().classes('w-full gap-4 flex-wrap items-stretch')
        main_row = ui.row().classes('w-full gap-6 mt-6').style('align-items: stretch')

        def renderizar_dashboard():
            data = get_all_mock_data()
            clientes = data["clientes"]
            inventario = data["inventario"]
            ventas = data["ventas"]
            soporte = data["soporte"]
            robots = data["robots"]

            total_ventas = sum(v["total"] for v in ventas)
            total_clientes = len(clientes)
            total_stock = sum(item["stock"] for item in inventario)
            soportes_abiertos = len([s for s in soporte if s["estado"] in ("Abierto", "Pendiente")])

            cards_container.clear()
            with cards_container:
                def crear_tarjeta(titulo, valor, icono, color):
                    with ui.card().classes(f'flex-1 min-w-[200px] bg-[#0a1e28] border-l-[6px] border-[{color}] p-4'):
                        with ui.column().classes('h-full justify-center rounded-r-lg'):
                            with ui.row().classes('items-center gap-2 w-full'):
                                ui.icon(icono, size='1.5rem', color=color)
                                ui.label(titulo).classes('text-sm font-bold text-[#d0f0f5] uppercase tracking-wider')
                            ui.label(valor).classes('text-3xl font-bold text-[#ffffff] mt-3 w-full')

                crear_tarjeta('VENTAS TOTALES', f'${format_number_abbreviated(total_ventas)}', 'attach_money', '#2dd4bf')
                crear_tarjeta('CLIENTES', f'{total_clientes:,}', 'people', '#67e8f9')
                crear_tarjeta('UDS. EN STOCK', f'{format_number_abbreviated(total_stock)}', 'inventory_2', '#2dd4bf')
                crear_tarjeta('SOPORTES ABIERTOS', f'{soportes_abiertos}', 'support_agent', '#f87171')

            main_row.clear()
            with main_row:
                with ui.column().classes('flex-2 min-w-[400px] h-full'):
                    with ui.card().classes('w-full h-full bg-[#0a1e28] p-4 flex flex-col'):
                        with ui.row().classes('items-center gap-2 mb-4'):
                            ui.icon('receipt', color='#1aabb8')
                            ui.label('Últimas ventas').classes('text-lg font-bold text-[#d0f0f5]')

                        ultimas_ventas = sorted(ventas, key=lambda x: x.get('fecha_venta', ''), reverse=True)[:15]

                        with ui.column().classes('flex-1 overflow-y-auto w-full gap-2'):
                            with ui.row().classes('w-full text-xs text-[#6b9caa] uppercase font-bold border-b border-[#1aabb8]/20 pb-2'):
                                ui.label('#').classes('w-12')
                                ui.label('CLIENTE').classes('flex-1')
                                ui.label('FECHA').classes('w-32')
                                ui.label('TOTAL').classes('w-32 text-right')

                            for idx, venta in enumerate(ultimas_ventas, 1):
                                cliente_nombre = next((c['nombre'] for c in clientes if c['nit'] == venta.get('id_cliente', '')), 'Desconocido')
                                fecha = str(venta.get('fecha_venta', ''))[:10]
                                with ui.row().classes('w-full py-2 border-b border-[#1aabb8]/10 hover:bg-[#0d2535] transition-colors'):
                                    ui.label(f'#{idx:03d}').classes('w-12 text-[#6b9caa] font-mono text-sm')
                                    ui.label(cliente_nombre).classes('flex-1 text-[#d0f0f5] text-sm')
                                    ui.label(fecha).classes('w-32 text-[#6b9caa] text-sm')
                                    ui.label(f'${venta["total"]:,.0f}').classes('w-32 text-right text-[#1aabb8] font-bold text-sm')

                with ui.column().classes('flex-1 min-w-[300px] gap-4 h-full w-full'):
                    with ui.card().classes('w-full bg-[#0a1e28] p-4 flex-1'):
                        with ui.row().classes('items-center gap-2 mb-3'):
                            ui.icon('warning', color='#ffd93d')
                            ui.label('Bajo stock').classes('text-lg font-bold text-[#d0f0f5]')

                        bajo_stock = [item for item in inventario if item.get('stock', 0) < 5]
                        if bajo_stock:
                            for item in bajo_stock[:3]:
                                nombre_modelo = next((r['nombre'] for r in robots if r['id'] == item.get('id_robot', '')), str(item.get('id', '')))
                                with ui.row().classes('w-full p-2 rounded bg-[#1a1a1a]/50 mb-2'):
                                    with ui.column().classes('flex-1'):
                                        ui.label(nombre_modelo).classes('text-sm font-bold text-[#d0f0f5]')
                                        ui.label(f'{item["stock"]} unidades').classes('text-xs text-[#ff6b6b]')
                        else:
                            ui.label('✅ No hay productos con bajo stock').classes('text-sm text-[#6b9caa]')

                    with ui.card().classes('w-full bg-[#0a1e28] p-4 flex-1'):
                        with ui.row().classes('items-center gap-2 mb-3'):
                            ui.icon('support_agent', color='#1aabb8')
                            ui.label('Soporte reciente').classes('text-lg font-bold text-[#d0f0f5]')

                        ultimos_soportes = sorted(soporte, key=lambda x: x.get('fecha_actualizacion', ''), reverse=True)[:6]

                        with ui.column().classes('w-full gap-2 flex-1'):
                            with ui.row().classes('w-full text-xs text-[#6b9caa] uppercase font-bold pb-1'):
                                ui.label('CLIENTE').classes('flex-1')
                                ui.label('ESTADO').classes('w-24')

                            for ticket in ultimos_soportes:
                                cliente_nombre = next((c['nombre'] for c in clientes if c['nit'] == ticket.get('id_cliente', '')), 'Desconocido')
                                estado = ticket.get('estado', '')
                                color_map = {
                                    'Abierto': '#ff6b6b',
                                    'Pendiente': '#ff6b6b',
                                    'En progreso': '#ffd93d',
                                    'En proceso': '#ffd93d',
                                    'Resuelto': '#1aabb8',
                                    'Cerrado': '#6b9caa',
                                    'Cancelado': '#6b9caa',
                                }
                                bg_color = color_map.get(estado, '#6b9caa')

                                with ui.row().classes('w-full py-2 border-b border-[#1aabb8]/10'):
                                    ui.label(cliente_nombre).classes('flex-1 text-[#d0f0f5] text-sm')
                                    ui.label(estado).classes('w-24 text-xs font-bold px-2 py-1 rounded-full text-center').style(
                                        f'background: {bg_color}22; color: {bg_color}; border: 1px solid {bg_color}44'
                                    )

        async def _cargar():
            if GAS_URL:
                await _cargar_datos_desde_gas()
            renderizar_dashboard()

        ui.timer(0.1, lambda: asyncio.ensure_future(_cargar()), once=True)
        ui.timer(3.0, renderizar_dashboard)
