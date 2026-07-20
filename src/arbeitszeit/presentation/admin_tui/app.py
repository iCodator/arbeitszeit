"""Admin-TUI-Einstiegspunkt."""

__version__ = "1.0"

from textual.app import App, ComposeResult


class AdminTuiApp(App[None]):
    def compose(self) -> ComposeResult:
        yield from ()


def main() -> None:
    AdminTuiApp().run()
