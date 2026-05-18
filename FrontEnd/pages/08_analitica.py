# FrontEnd/pages/08_analitica.py
from nicegui import ui
from mock_data import get_all_mock_data
import pandas as pd

def page(container: ui.column):
    with container:
        ui.label("Analítica").classes("page-title")
        ui.label("Reportes estratégicos y análisis de negocio").classes("page-subtitle").style(
            "margin-bottom: 24px;"
        )

        data = get_all_mock_data()
        df_ventas = pd.DataFrame(data["ventas"])
        df_detalle = pd.DataFrame(data["detalle_ventas"])
        df_inventario = pd.DataFrame(data["inventario"])
        df_robots = pd.DataFrame(data["robots"])
        df_clientes = pd.DataFrame(data["clientes"])
        df_soporte = pd.DataFrame(data["soporte"])

        # Robots más vendidos
        with ui.card().classes("w-full bg-[#0a1e28] border border-[rgba(26,171,184,0.2)] rounded-2xl p-4 mb-6"):
            ui.label("🤖 Robots más vendidos").classes("text-lg font-bold text-[#4dd9e6] mb-4")
            detalle_con_robot = (
                df_detalle
                .merge(df_inventario[["id", "id_robot"]], left_on="id_inventario", right_on="id")
                .merge(df_robots[["id", "nombre"]], left_on="id_robot", right_on="id")
            )
            resumen_robots = (
                detalle_con_robot.groupby("nombre")
                .agg(unidades=("cantidad", "sum"), ingresos=("subtotal", "sum"))
                .reset_index()
                .sort_values("unidades", ascending=False)
                .head(5)
            )
            total_ingresos = resumen_robots["ingresos"].sum()
            resumen_robots["participacion"] = (resumen_robots["ingresos"] / total_ingresos * 100).round(1)

            with ui.row().classes("w-full text-xs text-[#6b9caa] uppercase font-bold border-b border-[#1aabb8]/20 pb-2 mb-2"):
                ui.label("POS.").classes("w-12")
                ui.label("ROBOT").classes("flex-1")
                ui.label("UNIDADES").classes("w-24 text-center")
                ui.label("INGRESOS").classes("w-32 text-right")
                ui.label("PARTICIPACIÓN").classes("w-48 text-right")

            iconos = ["🚀", "🔥", "🏆"]
            for idx, (_, row) in enumerate(resumen_robots.iterrows()):
                pos = f"{iconos[idx]}  {idx+1}" if idx < 3 else f"#{idx+1}"
                with ui.row().classes("w-full py-2 border-b border-[#1aabb8]/10 items-center"):
                    ui.label(pos).classes("w-12 text-[#4dd9e6] font-bold")
                    ui.label(row["nombre"]).classes("flex-1 text-[#d0f0f5]")
                    ui.label(str(int(row["unidades"]))).classes("w-24 text-center text-[#d0f0f5]")
                    ui.label(f"${row['ingresos']:,.0f}".replace(",", ".")).classes("w-32 text-right text-[#1aabb8] font-bold")
                    with ui.column().classes("w-48 items-end gap-1"):
                        ui.label(f"{row['participacion']}%").classes("text-xs text-[#4dd9e6]")
                        ui.linear_progress(value=row['participacion'] / 100, show_value=False).classes("w-full").style("height: 6px; background-color: #1aabb8;")

        # Dos columnas: clientes y soporte
        with ui.row().classes("w-full gap-6"):
            with ui.column().classes("flex-1"):
                with ui.card().classes("w-full bg-[#0a1e28] border border-[rgba(26,171,184,0.2)] rounded-2xl p-4"):
                    ui.label("👥 Clientes con mayor facturación").classes("text-lg font-bold text-[#4dd9e6] mb-4")
                    ventas_group = (
                        df_ventas.groupby("id_cliente")
                        .agg(cantidad_ventas=("id", "count"), total_gastado=("total", "sum"))
                        .reset_index()
                        .merge(df_clientes[["nit", "nombre"]], left_on="id_cliente", right_on="nit")
                        .sort_values("total_gastado", ascending=False)
                        .head(5)
                    )
                    filas_clientes = []
                    for _, row in ventas_group.iterrows():
                        filas_clientes.append({
                            "cliente": row["nombre"],
                            "ventas": int(row["cantidad_ventas"]),
                            "total": f"${row['total_gastado'] / 1_000_000:.1f}M".replace(".", ","),
                        })
                    columnas_clientes = [
                        {"name": "cliente", "label": "CLIENTE", "field": "cliente"},
                        {"name": "ventas", "label": "VENTAS", "field": "ventas", "align": "center"},
                        {"name": "total", "label": "TOTAL", "field": "total", "align": "right"},
                    ]
                    ui.table(columns=columnas_clientes, rows=filas_clientes, row_key="cliente").classes("w-full").style("background: transparent;")

            with ui.column().classes("flex-1"):
                with ui.card().classes("w-full bg-[#0a1e28] border border-[rgba(26,171,184,0.2)] rounded-2xl p-4"):
                    ui.label("🛠️ Estado del soporte técnico").classes("text-lg font-bold text-[#4dd9e6] mb-4")
                    conteo = df_soporte["estado"].value_counts().to_dict()
                    total_tickets = len(df_soporte)
                    with ui.row().classes("w-full gap-4 flex-wrap justify-between"):
                        for estado, color in [("Resuelto", "green-400"), ("En proceso", "yellow-400"), ("Pendiente", "orange-400"), ("Cancelado", "red-400")]:
                            with ui.card().classes("flex-1 min-w-[100px] bg-[#0d2535] p-3 text-center"):
                                ui.label(estado.upper()).classes("text-xs text-[#6b9caa]")
                                ui.label(str(conteo.get(estado, 0))).classes(f"text-2xl font-bold text-{color}")
                        with ui.card().classes("flex-1 min-w-[100px] bg-[#0d2535] p-3 text-center"):
                            ui.label("TOTAL").classes("text-xs text-[#6b9caa]")
                            ui.label(str(total_tickets)).classes("text-2xl font-bold text-blue-400")