# components/table.py
from nicegui import ui
from typing import List, Dict, Optional, Callable


class SmartTable:
    """
    Tabla inteligente para NiceGUI/Quasar.

    REGLAS CLAVE:
    - Quasar recibe SIEMPRE todos los datos filtrados (nunca un slice).
    - La paginación la maneja Quasar con el objeto `pagination`.
    - Los botones de acción usan $parent.$emit desde el slot, que sube
      al q-table (el elemento que NiceGUI monitorea con table.on()).

    ÁRBOL VUE (por qué $parent.$emit):
        q-table  ← NiceGUI registra listeners aquí con table.on()
          └── slot scope component  ← contexto interno de Quasar
                └── q-td
                      └── q-btn  @click → $parent.$emit(...)  ✅
    """

    def __init__(
        self,
        columns: List[Dict],
        data: List[Dict] = None,
        title: str = "",
        subtitle: str = "",
        rows_per_page: int = 10,
        show_pagination: bool = True,
        show_actions: bool = True,
        action_buttons: Dict[str, Dict] = None,
        on_row_click: Optional[Callable] = None,
        on_action: Optional[Callable] = None,
        max_height: str = "600px",
        striped: bool = True,
        dense: bool = False,
        filterable: bool = True,
        row_key: str = "id",
        container_class: str = "",
        table_id: str = None,
    ):
        self.columns = columns
        self.original_data = data or []
        self.rows_per_page = rows_per_page
        self.title = title
        self.subtitle = subtitle
        self.show_pagination = show_pagination
        self.show_actions = show_actions
        self.action_buttons = action_buttons or {}
        self.on_row_click = on_row_click
        self.on_action = on_action
        self.max_height = max_height
        self.striped = striped
        self.dense = dense
        self.filterable = filterable
        self.row_key = row_key
        self.container_class = container_class
        self.table_id = table_id or f"table_{id(self)}"

        # Estado interno
        self.filtered_data: List[Dict] = []
        self.column_filters: Dict[str, str] = {
            col["field"]: ""
            for col in self.columns
            if col.get("filterable", True)
        }
        self.sort_column: Optional[str] = None
        self.sort_ascending: bool = True

        # Referencias a widgets
        self.container = None
        self.table = None
        self.filter_inputs: Dict[str, ui.input] = {}

        self._apply_filters()

    # ──────────────────────────────────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────────────────────────────────

    def build(self) -> ui.card:
        with ui.card() as self.container:
            self.container.classes(f"w-full {self.container_class}").style(
                "background: var(--bg-card); "
                "border: 1px solid var(--border); "
                "border-radius: 16px; "
                "padding: 20px; "
                "overflow: hidden;"
            )

            if self.title:
                ui.label(self.title).classes("text-h5 font-bold").style(
                    "color: var(--teal-light)"
                )
            if self.subtitle:
                ui.label(self.subtitle).classes("text-caption").style(
                    "color: var(--text-muted)"
                )
                ui.separator().classes("my-2").style("background: var(--border)")

            # ── Filtros por columna ──────────────────────────────────
            if self.filterable:
                with ui.row().classes("flex-wrap gap-2 mb-2"):
                    for col in self.columns:
                        if col.get("filterable", True):
                            field = col["field"]
                            label = col["label"]
                            self.filter_inputs[field] = (
                                ui.input(
                                    placeholder=f"Filtrar {label}...",
                                    on_change=lambda v, f=field: self._on_column_filter(
                                        f, v.value
                                    ),
                                )
                                .props("dense outlined")
                                .classes("w-36")
                                .style(
                                    "background: var(--bg-panel) !important; "
                                    "color: var(--text-main) !important;"
                                )
                            )

            # ── Tabla ────────────────────────────────────────────────
            with ui.element("div").style(
                f"overflow-x: auto; max-height: {self.max_height};"
            ):
                self.table = ui.table(
                    columns=self._build_quasar_columns(),
                    rows=self.filtered_data,
                    row_key=self.row_key,
                    pagination={
                        "rowsPerPage": self.rows_per_page if self.show_pagination else 0,
                        "page": 1,
                    },
                ).classes("w-full").style(
                    "background: transparent; color: var(--text-main);"
                )

                if self.dense:
                    self.table.props("dense")
                self.table.props("bordered")
                if self.striped:
                    self.table.props("striped")
                if self.show_pagination:
                    self.table.props("hide-bottom=false")
                else:
                    self.table.props("hide-bottom")

                if self.on_row_click:
                    self.table.on("rowClick", lambda e: self._handle_row_click(e))

                # Slot de acciones con $parent.$emit
                if self.show_actions and self.action_buttons:
                    self._build_action_slot()

        return self.container

    # ──────────────────────────────────────────────────────────────────
    # Slot de acciones — fix: $parent.$emit sube al q-table
    # ──────────────────────────────────────────────────────────────────

    def _build_action_slot(self):
        """
        Construye el slot body-cell-actions con botones q-btn.

        FIX CRÍTICO: usar $parent.$emit en lugar de $emit.

        Dentro del slot, el contexto Vue es un componente interno de
        Quasar (un scope slot component), NO el q-table en sí mismo.
        NiceGUI registra los listeners en el q-table, que es el
        $parent de ese componente interno. Por eso:

            $emit(...)          → evento en el hijo  → NiceGUI NO lo ve  ❌
            $parent.$emit(...)  → evento en q-table  → NiceGUI SÍ lo ve  ✅

        @click.stop previene que el clic burbujee y dispare rowClick
        simultáneamente con la acción del botón.
        """
        buttons_html = ""
        for action_name, config in self.action_buttons.items():
            icon    = config.get("icon", "settings")
            color   = config.get("color", "grey")
            tooltip = config.get("tooltip", action_name)

            buttons_html += f"""
            <q-btn flat round dense
                   icon="{icon}"
                   color="{color}"
                   size="sm"
                   :ripple="false"
                   title="{tooltip}"
                   @click.stop="$parent.$emit('table-action', {{
                       action:   '{action_name}',
                       key:      String(props.row['{self.row_key}']),
                       table_id: '{self.table_id}'
                   }})"
            />
            """

        self.table.add_slot("body-cell-actions", f"""
            <q-td :props="props" style="text-align:center; white-space:nowrap; padding:4px 8px;">
                {buttons_html}
            </q-td>
        """)

        # El listener va en self.table (el q-table = $parent del slot)
        self.table.on("table-action", self._handle_table_action)

    def _handle_table_action(self, event):
        """
        Recibe el evento emitido por $parent.$emit desde el slot.
        event.args es el diccionario con action, key y table_id.
        """
        datos = event.args
        action = datos.get("action")
        key    = datos.get("key")
        self._dispatch_action(action, key)

    def _dispatch_action(self, action_name: str, row_key_value):
        """Busca la fila por clave y llama a on_action."""
        if not self.on_action:
            return
        fila = next(
            (r for r in self.filtered_data
             if str(r.get(self.row_key)) == str(row_key_value)),
            None,
        )
        if fila:
            self.on_action(action_name, fila)

    # ──────────────────────────────────────────────────────────────────
    # Columnas Quasar
    # ──────────────────────────────────────────────────────────────────

    def _build_quasar_columns(self) -> List[Dict]:
        cols = []
        for col in self.columns:
            cols.append({
                "name":     col["field"],
                "label":    col["label"],
                "field":    col["field"],
                "sortable": col.get("sortable", True),
                "align":    col.get("align", "left"),
                "style":    f"width: {col.get('width', 'auto')};",
            })

        if self.show_actions and self.action_buttons:
            btn_count = len(self.action_buttons)
            col_width = max(80, btn_count * 52)
            cols.append({
                "name":     "actions",
                "label":    "Acciones",
                "field":    "actions",
                "sortable": False,
                "align":    "center",
                "style":    f"width: {col_width}px; min-width: 80px;",
            })
        return cols

    # ──────────────────────────────────────────────────────────────────
    # Filtrado y ordenamiento
    # ──────────────────────────────────────────────────────────────────

    def _apply_filters(self):
        result = self.original_data.copy()

        filter_modes = {
            col["field"]: col.get("filter_mode", "contains")
            for col in self.columns
        }

        for field, value in self.column_filters.items():
            if value:
                lower = value.lower()
                mode  = filter_modes.get(field, "contains")
                if mode == "exact":
                    result = [r for r in result if str(r.get(field, "")).lower() == lower]
                elif mode == "startswith":
                    result = [r for r in result if str(r.get(field, "")).lower().startswith(lower)]
                else:
                    result = [r for r in result if lower in str(r.get(field, "")).lower()]

        if self.sort_column:
            result.sort(
                key=lambda x: x.get(self.sort_column, ""),
                reverse=not self.sort_ascending,
            )

        self.filtered_data = result

    def _on_column_filter(self, field: str, value: str):
        self.column_filters[field] = value
        self._apply_filters()
        self._push_to_table()

    def _handle_row_click(self, event):
        if self.on_row_click:
            self.on_row_click(event.args[0]["row"])

    # ──────────────────────────────────────────────────────────────────
    # Actualización reactiva
    # ──────────────────────────────────────────────────────────────────

    def _push_to_table(self):
        if self.table is None:
            return
        self.table.rows = self.filtered_data
        self.table.pagination = {**self.table.pagination, "page": 1}

    def refresh(self):
        """Re-aplica filtros y empuja los datos al frontend."""
        self._apply_filters()
        self._push_to_table()

    def set_data(self, new_data: List[Dict]):
        """Reemplaza el dataset completo y refresca la tabla."""
        self.original_data = new_data
        self.refresh()