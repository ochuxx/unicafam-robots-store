from nicegui import ui
from typing import Callable, Optional, List, Any, Union, Dict, Tuple
import re

class SmartForm:
    """
    Formulario dinámico con diseño en cuadrícula y validación MANUAL.
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
        cancel_text: str = "Cancelar",
        max_length: Optional[int] = None,
        enable_validation: bool = True,
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
        self.max_length = max_length
        self.enable_validation = enable_validation

        self.fields: List[Tuple[ui.element, str, str, bool, Optional[int], List]] = []
        self.container = None
        self.grid_container = None

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
        max_length: Optional[int] = None,
        validation: Optional[Union[Callable, Dict]] = None,
        integer_only: bool = False,
        **kwargs
    ):
        with self.grid_container:
            with ui.element('div').style('width: 100%;'):
                if label:
                    ui.label(label).classes('text-sm font-medium mb-1').style('color: var(--text-muted);')

                field = None
                char_limit = max_length if max_length is not None else self.max_length

                # ----- Crear el campo -----
                if field_type == "input":
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                    if char_limit is not None:
                        field.props(f'maxlength={char_limit}')

                elif field_type == "textarea":
                    field = ui.textarea(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                    if rows > 1:
                        field.props(f'rows={rows}')
                    if char_limit is not None:
                        field.props(f'maxlength={char_limit}')

                elif field_type == "select":
                    field = ui.select(options=options or [], value=value, on_change=on_change, **kwargs)

                elif field_type == "number":
                    num_value = None if value in (None, '') else value
                    if integer_only:
                        # Configurar para solo enteros
                        field = ui.number(
                            value=num_value,
                            placeholder=placeholder,
                            on_change=on_change,
                            step=1,
                            precision=0,
                            **kwargs
                        )
                    else:
                        field = ui.number(
                            value=num_value,
                            placeholder=placeholder,
                            on_change=on_change,
                            **kwargs
                        )

                elif field_type == "date":
                    field = ui.input(value=value, on_change=on_change, **kwargs)
                    field.props('type=date')

                elif field_type == "email":
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                    field.props('type=email')
                    if char_limit is not None:
                        field.props(f'maxlength={char_limit}')

                elif field_type == "password":
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                    field.props('type=password')
                    if char_limit is not None:
                        field.props(f'maxlength={char_limit}')

                else:
                    field = ui.input(value=value, placeholder=placeholder, on_change=on_change, **kwargs)
                    if char_limit is not None:
                        field.props(f'maxlength={char_limit}')

                # ----- Construir reglas de validación -----
                validation_rules = []
                if self.enable_validation:
                    if required:
                        validation_rules.append(('required', None))
                    if field_type == "email":
                        validation_rules.append(('email_format', None))
                    elif field_type == "date":
                        validation_rules.append(('date', None))
                    if validation:
                        validation_rules.append(('custom', validation))
                    # Para campos number con integer_only=True, agregar validación de entero
                    if field_type == "number" and integer_only:
                        validation_rules.append(('integer', None))
                    elif field_type == "number" and not integer_only:
                        validation_rules.append(('number', None))

                # ----- Estilos comunes -----
                if field:
                    field.classes('w-full').style('''
                        background: var(--bg-panel) !important;
                        color: var(--text-main) !important;
                        border: 1px solid var(--border);
                        border-radius: 8px;
                        padding: 8px 12px;
                    ''')
                    field.props('outlined dense')
                    self.fields.append((field, label, field_type, required, char_limit, validation_rules))

        return field

    # --------------------------------------------------------------
    # Validación manual
    # --------------------------------------------------------------
    def _validate_field(self, field, value, field_type, required, char_limit, rules) -> Optional[str]:
        # 1. Requerido
        if required:
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return "Este campo es obligatorio"

        # Si no es requerido y está vacío, salir
        if not required and (value is None or (isinstance(value, str) and value.strip() == "")):
            return None

        # 2. Longitud máxima (solo strings)
        if char_limit and isinstance(value, str) and len(value) > char_limit:
            return f"Máximo {char_limit} caracteres"

        # 3. Validaciones por regla
        for rule, param in rules:
            if rule == 'email_format':
                if value and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                    return "Ingrese un correo electrónico válido (ej: usuario@dominio.com)"
            elif rule == 'number':
                try:
                    float(value)
                except (ValueError, TypeError):
                    return "Solo se permiten caracteres numéricos"
            elif rule == 'integer':
                # Validar que sea un número entero (sin decimales)
                try:
                    num = float(value)
                    if num != int(num):
                        return "Solo se permiten números enteros (sin punto decimal)"
                except (ValueError, TypeError):
                    return "Debe ingresar un número entero válido"
            elif rule == 'date':
                if value and not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                    return "Formato de fecha inválido. Use YYYY-MM-DD"
            elif rule == 'custom':
                if callable(param):
                    res = param(value)
                    if res is not True:
                        return str(res)
                elif isinstance(param, dict):
                    try:
                        num = float(value)
                        if 'min' in param and num < param['min']:
                            return f"El valor debe ser mayor o igual a {param['min']}"
                        if 'max' in param and num > param['max']:
                            return f"El valor debe ser menor o igual a {param['max']}"
                    except:
                        return "Debe ser un número válido"
        return None

    def _clear_field_error(self, field):
        if hasattr(field, 'set_error'):
            field.set_error(None)
        elif hasattr(field, 'error'):
            field.error = None

    def _set_field_error(self, field, message):
        if hasattr(field, 'set_error'):
            field.set_error(message)
        elif hasattr(field, 'error'):
            field.error = message

    def is_valid(self) -> bool:
        all_valid = True
        for field, label, field_type, required, char_limit, rules in self.fields:
            error_msg = self._validate_field(field, field.value, field_type, required, char_limit, rules)
            if error_msg:
                self._set_field_error(field, error_msg)
                all_valid = False
            else:
                self._clear_field_error(field)
        return all_valid

    def clear_errors(self):
        for field, *_ in self.fields:
            self._clear_field_error(field)

    def get_values(self) -> dict:
        return {f"field_{i}": field.value for i, (field, *_) in enumerate(self.fields)}

    def get_values_with_labels(self) -> dict:
        return {label: field.value for field, label, *_, in self.fields if label}