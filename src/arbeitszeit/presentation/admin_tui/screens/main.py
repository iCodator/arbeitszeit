"""MainScreen (Platzhalter — wird in Schritt 4 vollständig implementiert)."""

__version__ = "1.0"

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label

from .._connection import AppState


class MainScreen(Screen[None]):
    BINDINGS = [("q", "app.quit", "Beenden")]

    def __init__(self, state: AppState) -> None:
        super().__init__()
        self._state = state

    def compose(self) -> ComposeResult:
        yield Label(
            f"Verbunden: {self._state.db_path}  |  Benutzer-ID: {self._state.user_id}"
        )
        yield Label("MainScreen — Schritt 4 folgt  |  q = Beenden")
