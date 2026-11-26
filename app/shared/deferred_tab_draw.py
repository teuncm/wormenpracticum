from collections.abc import Callable

from PySide6.QtWidgets import QTabWidget, QWidget


class DeferredTabDraw:
    """Coalesce hidden tab updates into one draw when that tab is selected."""

    def __init__(
        self,
        draw: Callable[[], None],
        page: QWidget | None,
        tabs: QTabWidget | None = None,
    ):
        self._draw = draw
        self._tabs = tabs
        self._page = page
        self._pending = False

        if tabs is not None:
            tabs.currentChanged.connect(self._draw_if_active)

    def request(self) -> None:
        self._pending = True
        self._draw_if_active()

    def _draw_if_active(self) -> None:
        if not self._pending:
            return
        if self._tabs is not None and self._tabs.currentWidget() is not self._page:
            return

        self._pending = False
        self._draw()
