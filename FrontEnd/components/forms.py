# FrontEnd/components/forms.py
from nicegui import ui
from typing import Callable, Optional, List, Any

class SmartForm:
    """
    Formulario dinámico con diseño en cuadrícula (CSS Grid) y botones opcionales.

    Permite agregar campos de distintos tipos (input, textarea, select, etc.)
    y obtener sus valores. El contenedor principal es una tarjeta de NiceGUI.
    """

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
        """
        Inicializa el SmartForm.

        :param title: Título del formulario (opcional).
        :param subtitle: Subtítulo (opcional).
        :param padding: Padding interno de la tarjeta.
        :param gap: Espaciado entre columnas del grid.
        :param columns: Número de columnas del grid (CSS grid).
        :param max_width: Ancho máximo de la tarjeta (ej: '600px').
        :param submit_callback: Función a ejecutar al pulsar "Guardar".
        :param cancel_callback: Función a ejecutar al pulsar "Cancelar".
        :param submit_text: Texto del botón de guardado.
        :param cancel_text: Texto del botón de cancelación.
        """
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

        self.fields = []                # Lista de componentes de campo generados
        self.container = None           # Tarjeta principal (se crea en build)
        self.grid_container = None      # Contenedor interno con display: grid

    def build(self) -> ui.card:
        """
        Construye y retorna la tarjeta del formulario con todos sus elementos.
        Debe llamarse después de agregar los campos (add_field) para mostrarlos.

        :return: Componente ui.card que contiene el formulario.
        """
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
        """
        Agrega un campo al formulario (dentro de la cuadrícula).

        :param field_type: Tipo de campo ('input', 'textarea', 'select', 'number', 'date', 'email', 'password').
        :param label: Etiqueta del campo.
        :param placeholder: Texto de placeholder.
        :param value: Valor inicial.
        :param required: Si es obligatorio (no se aplica validación automática).
        :param rows: Número de filas (solo para textarea).
        :param options: Lista de opciones (solo para select).
        :param on_change: Callback al cambiar el valor.
        :param kwargs: Argumentos adicionales pasados al componente NiceGUI.
        :return: El componente de campo creado (ui.input, ui.select, etc.).
        """
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
                    field = ui.input(value=value, on_change=on_change, **kwargs)
                    field.props('type=date')
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
        """
        Obtiene los valores actuales de todos los campos del formulario.

        :return: Diccionario con claves 'field_0', 'field_1', ... y sus respectivos valores.
        """
        return {f"field_{i}": f.value for i, f in enumerate(self.fields)}