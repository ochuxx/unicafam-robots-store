from nicegui import ui
import asyncio


class LoadingOverlay:
    def __init__(self):
        self.element = None

    def build(self):
        self.element = ui.element('div')
        self.element.style(
            'position: fixed; inset: 0; display: none; '
            'align-items: center; justify-content: center; '
            'background: rgba(0,0,0,0.55); z-index: 9999;'
        )
        with self.element:
            with ui.row().classes('items-center gap-4').style(
                'background: #1a1a2e; border-radius: 12px; padding: 24px 32px;'
            ):
                ui.spinner('dots', size='xl', color='teal')
                ui.label('Procesando...').style('color: white; font-size: 1.2rem;')
        return self.element

    def show(self):
        if self.element:
            self.element.style('display: flex;')

    def hide(self):
        if self.element:
            self.element.style('display: none;')


async def with_spinner(
    loading: LoadingOverlay,
    action,
    *,
    refresh=None,
    delay: float = 0.05,
    loading_after_action: bool = False,
):
    loading.show()
    await asyncio.sleep(delay)
    try:
        result = action() if not asyncio.iscoroutinefunction(action) else await action()
        if loading_after_action:
            loading.show()
            await asyncio.sleep(delay)
        if refresh:
            if asyncio.iscoroutinefunction(refresh):
                await refresh()
            else:
                refresh()
        return result
    finally:
        loading.hide()
