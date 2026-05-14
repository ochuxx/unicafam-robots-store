# FrontEnd/components/forms.py
from nicegui import ui
from typing import Callable, Optional, List, Any

class SmartForm:
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        padding: str = "20px",
        gap: str = "16px",
        columns: int = 1,
        max_width: str = "100%",
        submit_callback: Optional[Callable] = None,
        cancel_callback: Optional[Callable] = None,
        submit_text: str = "Guardar",
        cancel_text: str = "Cancelar"
    ):
        self.title = title
        self.subtitle = subtitle
        self.padding = padding
        self.gap = gap
        self.columns = columns
        self.max_width = max_width
        self.submit_callback = submit_callback
        self.cancel_callback = cancel_callback
        self.submit_text = submit_text
        self.cancel_text = cancel_text

        self.fields = []
        self.container = None
        self.grid_container = None   # Nuevo: contenedor grid
        self.field_count = 0

    def build(self) -> ui.card:
        with ui.card() as self.container:
            self.container.classes('w-full').style(
                f'background: var(--bg-card); '
                f'border: 1px solid var(--border); '
                f'border-radius: 16px; '
                f'padding: {self.padding}; '
                f'max-width: {self.max_width};'
            )

            if self.title:
                ui.label(self.title).classes('text-h5 font-bold').style('color: var(--teal-light)')
            if self.subtitle:
                ui.label(self.subtitle).classes('text-caption').style('color: var(--text-muted)')
                ui.separator().classes('my-2').style('background: var(--border)')

            # Usamos CSS Grid para un control exacto de columnas
            self.grid_container = ui.element('div').style(
                f'display: grid; '
                f'grid-template-columns: repeat({self.columns}, 1fr); '
                f'gap: {self.gap}; '
                f'width: 100%;'
            )

            if self.submit_callback or self.cancel_callback:
                with ui.row().classes('mt-4 gap-2 justify-end'):
                    if self.cancel_callback:
                        ui.button(self.cancel_text, on_click=self.cancel_callback) \
                          .props('flat').classes('text-white').style('background: transparent; border: 1px solid var(--teal-mid);')
                    if self.submit_callback:
                        ui.button(self.submit_text, on_click=self.submit_callback) \
                          .props('unelevated').classes('text-white').style('background: var(--teal-mid);')
        return self.container

    def add_field(
        self,
        field_type: str = "input",
        label: str = "",
        placeholder: str = "",
        value: Any = None,
        required: bool = False,
        rows: int = 1,
        options: List[str] = None,
        on_change: Optional[Callable] = None,
        **kwargs
    ):
        # Cada campo ocupará una celda del grid
        with self.grid_container:
            with ui.element('div').style('width: 100%;'):
                if label:
                    ui.label(label).classes('text-sm font-medium mb-1').style('color: var(--text-muted);')

                field = None
                if field_type == "input":
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                elif field_type == "textarea":
                    field = ui.textarea(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                    if rows > 1:
                        field.props(f'rows={rows}')
                elif field_type == "select":
                    field = ui.select(options=options or [], value=value, on_change=on_change, **kwargs)
                elif field_type == "number":
                    num_value = None if value in (None, '') else value
                    field = ui.number(value=num_value, placeholder=placeholder, on_change=on_change, **kwargs)
                elif field_type == "date":
                    field = ui.date(value=value, on_change=on_change, **kwargs)
                elif field_type == "email":
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change).props('type=email')
                elif field_type == "password":
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change).props('type=password')
                else:
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change, **kwargs)

                if field:
                    field.classes('w-full').style('''
                        background: var(--bg-panel) !important;
                        color: var(--text-main) !important;
                        border: 1px solid var(--border);
                        border-radius: 8px;
                        padding: 8px 12px;
                    ''')
                    field.props('outlined dense')
                    self.fields.append(field)

        return field

    def get_values(self) -> dict:
        return {f"field_{i}": f.value for i, f in enumerate(self.fields)}