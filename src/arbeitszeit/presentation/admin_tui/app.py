"""Admin-TUI-Einstiegspunkt."""

__version__ = "1.1"

from textual.app import App, ComposeResult

from ._connection import load_app_config
from .screens.login import LoginScreen


class AdminTuiApp(App[None]):
    TITLE = "arbeitszeit Admin"

    def compose(self) -> ComposeResult:
        yield from ()

    def on_mount(self) -> None:
        cfg, cfg_error = load_app_config()
        self.push_screen(LoginScreen(cfg, cfg_error))


def main() -> None:
    AdminTuiApp().run()
