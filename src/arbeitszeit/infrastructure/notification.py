"""Desktop-Benachrichtigung via notify-send (Stdlib subprocess, kein neues Paket).

Pflichtenheft §7.10: Systemzustand muss dem Betreiber sichtbar sein.
Stilles Fail-Safe: wenn notify-send nicht verfügbar, passiert nichts.

Voraussetzung: libnotify-bin (auf Lubuntu/Linux Mint standardmäßig vorhanden).
"""

import logging
import subprocess

_NOTIFY_SEND = "/usr/bin/notify-send"


def notify(title: str, body: str, urgency: str = "normal") -> None:
    """Sendet Desktop-Notification. Schlägt still fehl wenn notify-send fehlt.

    urgency: "low" | "normal" | "critical"
    """
    try:
        subprocess.run(
            [_NOTIFY_SEND, f"--urgency={urgency}", "--app-name=Arbeitszeit", title, body],
            timeout=3,
            check=False,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logging.debug("notify-send nicht verfügbar — Benachrichtigung übersprungen.")
    except Exception as exc:
        logging.warning("notification.notify fehlgeschlagen: %s", exc)
