"""LoginScreen: Datenbankverbindung aufbauen."""

__version__ = "1.0"

import sqlite3
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from arbeitszeit.infrastructure.config_file import AppConfig

from .._connection import open_app_state, resolve_db_path, resolve_user_id
from .main import MainScreen


class LoginScreen(Screen[None]):
    CSS = """
    LoginScreen {
        align: center middle;
    }
    #login-box {
        width: 64;
        height: auto;
        border: solid $primary;
        padding: 1 2;
    }
    #title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #cfg-warning {
        color: $warning;
        margin-bottom: 1;
    }
    #error-msg {
        color: $error;
        margin-top: 1;
    }
    Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, cfg: AppConfig | None, cfg_error: str | None = None) -> None:
        super().__init__()
        self._cfg = cfg
        self._cfg_error = cfg_error

    def compose(self) -> ComposeResult:
        db_val = str(self._cfg.database.path) if self._cfg and self._cfg.database.path else ""
        uid_val = (
            str(self._cfg.admin.user_id)
            if self._cfg and self._cfg.admin.user_id is not None
            else ""
        )
        with Vertical(id="login-box"):
            yield Label("arbeitszeit Admin-TUI", id="title")
            if self._cfg_error:
                yield Label(f"Konfiguration: {self._cfg_error}", id="cfg-warning")
            yield Label("Datenbankpfad")
            yield Input(value=db_val, placeholder="/pfad/zur/arbeitszeit.db", id="db-path")
            yield Label("Benutzer-ID")
            yield Input(value=uid_val, placeholder="1", id="user-id")
            yield Button("Verbinden", id="connect", variant="primary")
            yield Label("", id="error-msg")

    @on(Button.Pressed, "#connect")
    def handle_connect(self, _: Button.Pressed) -> None:
        error_label = self.query_one("#error-msg", Label)
        db_raw = self.query_one("#db-path", Input).value.strip()
        uid_raw = self.query_one("#user-id", Input).value.strip()

        try:
            db_path = resolve_db_path(Path(db_raw) if db_raw else None, self._cfg)
        except ValueError as exc:
            error_label.update(str(exc))
            return

        try:
            parsed_uid = int(uid_raw) if uid_raw else None
        except ValueError:
            error_label.update("Benutzer-ID muss eine Ganzzahl sein.")
            return

        try:
            user_id = resolve_user_id(parsed_uid, self._cfg)
        except ValueError as exc:
            error_label.update(str(exc))
            return

        try:
            state = open_app_state(db_path, user_id, self._cfg)
        except (sqlite3.OperationalError, OSError) as exc:
            error_label.update(f"Datenbankfehler: {exc}")
            return

        error_label.update("")
        self.app.push_screen(MainScreen(state))
