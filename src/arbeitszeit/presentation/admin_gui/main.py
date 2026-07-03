"""Admin-GUI für arbeitszeit — tkinter/ttk-basierte Verwaltungsoberfläche.

Einstieg:
    python -m arbeitszeit.presentation.admin_gui.main

Die GUI richtet sich an technisch weniger erfahrene Praxisadministratorinnen
und -administratoren. Jede Schaltfläche und jedes Eingabefeld ist mit einem
ausführlichen Hilfstext versehen. Alle schreibenden Operationen werden über
die Use Cases der Anwendungsschicht abgewickelt.
"""

from __future__ import annotations

import binascii
import hashlib
import json
import os
import secrets
import sqlite3
import sys
import traceback
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

_SRC = Path(__file__).resolve().parents[4]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.errors import DomainError
from arbeitszeit.presentation.admin_gui.controller import (
    assign_rfid_card,
    bootstrap_admin,
    change_user_role,
    create_employee,
    create_user_account,
    deactivate_employee,
    deactivate_rfid_card,
    deactivate_user_account,
    reactivate_user_account,
    replace_rfid_card,
)
from arbeitszeit.infrastructure.backup.backup_service import SQLiteBackupService
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.migrations import run_migrations
from arbeitszeit.infrastructure.db.unit_of_work import SQLiteUnitOfWork
from arbeitszeit.infrastructure.system_check import run_system_check

# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """PBKDF2-HMAC-SHA256, 260 000 Iterationen, 16-Byte-Zufallssalt."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


def _make_uow(db_path: Path) -> tuple[SQLiteUnitOfWork, sqlite3.Connection, sqlite3.Connection]:
    conn = open_connection(db_path)
    audit_conn = open_connection(db_path)
    uow = SQLiteUnitOfWork(conn, audit_conn)
    return uow, conn, audit_conn


def _close(conn: sqlite3.Connection, audit_conn: sqlite3.Connection) -> None:
    conn.close()
    audit_conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Tooltip-Klasse
# ─────────────────────────────────────────────────────────────────────────────

class ToolTip:
    """Zeigt einen mehrzeiligen Hilfstext an, wenn der Mauszeiger über
    einem Widget verweilt. Verschwindet automatisch beim Verlassen."""

    def __init__(self, widget: tk.Widget, text: str, delay: int = 600) -> None:
        self._widget = widget
        self._text = text
        self._delay = delay
        self._id: str | None = None
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._cancel)
        widget.bind("<ButtonPress>", self._cancel)

    def _schedule(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self._cancel()
        self._id = self._widget.after(self._delay, self._show)

    def _cancel(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if self._id:
            self._widget.after_cancel(self._id)
            self._id = None
        if self._tip:
            self._tip.destroy()
            self._tip = None

    def _show(self) -> None:
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            self._tip,
            text=self._text,
            justify=tk.LEFT,
            background="#fffde7",
            foreground="#333",
            relief=tk.SOLID,
            borderwidth=1,
            font=("TkSmallCaptionFont", 0),
            wraplength=360,
            padx=6,
            pady=4,
        )
        lbl.pack()


def tip(widget: tk.Widget, text: str) -> ToolTip:
    """Kurzform: Hilfstext an ein Widget binden."""
    return ToolTip(widget, text)


# ─────────────────────────────────────────────────────────────────────────────
# Verbindungsdialog
# ─────────────────────────────────────────────────────────────────────────────

class VerbindungsDialog(tk.Toplevel):
    """Fragt beim Start nach Datenbankpfad und Benutzer-ID.

    Ohne gültige Verbindung bleibt die Anwendung im Demo-/Info-Modus.
    """

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.title("Arbeitszeit — Verbindung herstellen")
        self.resizable(False, False)
        self.grab_set()
        self.db_path: Path | None = None
        self.user_id: int | None = None
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._abbrechen)

    def _build(self) -> None:
        pad = {"padx": 12, "pady": 6}

        tk.Label(self, text="Arbeitszeit", font=("TkHeadingFont", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(18, 4)
        )
        tk.Label(self, text="Verwaltungsoberfläche", foreground="#555").grid(
            row=1, column=0, columnspan=3, pady=(0, 16)
        )

        # Datenbankpfad
        tk.Label(self, text="Datenbankdatei:", anchor="w").grid(
            row=2, column=0, sticky="w", **pad
        )
        self._db_var = tk.StringVar(value=str(Path.home() / "arbeitszeit" / "arbeitszeit.db"))
        db_entry = ttk.Entry(self, textvariable=self._db_var, width=38)
        db_entry.grid(row=2, column=1, sticky="ew", padx=(0, 4), pady=6)
        tip(db_entry, "Vollständiger Pfad zur SQLite-Datenbankdatei von arbeitszeit.")

        browse_btn = ttk.Button(self, text="…", width=3, command=self._durchsuchen)
        browse_btn.grid(row=2, column=2, padx=(0, 12), pady=6)
        tip(browse_btn, "Dateidialog öffnen und Datenbankdatei auswählen.")

        # Benutzer-ID
        tk.Label(self, text="Benutzer-ID:", anchor="w").grid(
            row=3, column=0, sticky="w", **pad
        )
        self._uid_var = tk.StringVar(value="1")
        uid_entry = ttk.Entry(self, textvariable=self._uid_var, width=10)
        uid_entry.grid(row=3, column=1, sticky="w", padx=(0, 4), pady=6)
        tip(
            uid_entry,
            "Ihre numerische Benutzer-ID (Zahl). Diese ID wird für alle "
            "schreibenden Operationen als ausführendes Konto verwendet.\n\n"
            "Nach dem ersten Bootstrap lautet die Admin-ID in der Regel 1.",
        )

        # Hinweistext
        info = (
            "Hinweis: Alternativ kann die Benutzer-ID über die Umgebungsvariable\n"
            "ADMIN_USER_ID gesetzt werden."
        )
        tk.Label(self, text=info, foreground="#666", justify=tk.LEFT).grid(
            row=4, column=0, columnspan=3, padx=12, pady=(0, 10), sticky="w"
        )

        # Schaltflächen
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=(6, 18))

        verbinden_btn = ttk.Button(btn_frame, text="Verbinden", command=self._verbinden)
        verbinden_btn.pack(side=tk.LEFT, padx=6)
        tip(verbinden_btn, "Verbindung zur Datenbank herstellen und Verwaltung öffnen.")
        verbinden_btn.focus_set()

        abbrechen_btn = ttk.Button(btn_frame, text="Abbrechen", command=self._abbrechen)
        abbrechen_btn.pack(side=tk.LEFT, padx=6)
        tip(abbrechen_btn, "Dialog schließen und Anwendung beenden.")

        self.bind("<Return>", lambda _: self._verbinden())
        self.bind("<Escape>", lambda _: self._abbrechen())

    def _durchsuchen(self) -> None:
        pfad = filedialog.askopenfilename(
            title="Datenbankdatei auswählen",
            filetypes=[("SQLite-Datenbank", "*.db"), ("Alle Dateien", "*")],
        )
        if pfad:
            self._db_var.set(pfad)

    def _verbinden(self) -> None:
        db_str = self._db_var.get().strip()
        uid_str = self._uid_var.get().strip()

        if not db_str:
            messagebox.showerror("Fehler", "Bitte einen Datenbankpfad angeben.", parent=self)
            return

        db = Path(db_str)
        if not db.exists():
            if not messagebox.askyesno(
                "Datenbank nicht gefunden",
                f"Die Datei '{db}' existiert nicht.\n"
                "Soll eine neue Datenbank angelegt werden?",
                parent=self,
            ):
                return
            try:
                db.parent.mkdir(parents=True, exist_ok=True)
                conn = open_connection(db)
                run_migrations(conn)
                conn.close()
            except Exception as exc:
                messagebox.showerror("Fehler", f"Datenbank konnte nicht angelegt werden:\n{exc}", parent=self)
                return
        else:
            try:
                conn = open_connection(db)
                run_migrations(conn)
                conn.close()
            except Exception as exc:
                messagebox.showerror("Verbindungsfehler", str(exc), parent=self)
                return

        try:
            user_id = int(uid_str) if uid_str else None
        except ValueError:
            messagebox.showerror("Fehler", "Benutzer-ID muss eine ganze Zahl sein.", parent=self)
            return

        self.db_path = db
        self.user_id = user_id
        self.destroy()

    def _abbrechen(self) -> None:
        self.db_path = None
        self.user_id = None
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Hilfsdialog
# ─────────────────────────────────────────────────────────────────────────────

class HilfeDialog(tk.Toplevel):
    """Zeigt einen allgemeinen Hilfetext als scrollbares Textfenster."""

    def __init__(self, parent: tk.Widget, titel: str, inhalt: str) -> None:
        super().__init__(parent)
        self.title(f"Hilfe — {titel}")
        self.resizable(True, True)
        self.geometry("600x440")
        text = tk.Text(self, wrap=tk.WORD, padx=12, pady=12, font=("TkDefaultFont", 0))
        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.insert("1.0", inhalt)
        text.configure(state=tk.DISABLED)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Schließen", command=self.destroy).pack(pady=8)
        self.bind("<Escape>", lambda _: self.destroy())


# ─────────────────────────────────────────────────────────────────────────────
# Eingabe-Hilfsdialog (einzeiliger Text)
# ─────────────────────────────────────────────────────────────────────────────

class EingabeFeld:
    """Hilfsklasse für Formulardialoge."""

    def __init__(
        self,
        frame: tk.Widget,
        row: int,
        label: str,
        hilfe: str,
        default: str = "",
        show: str = "",
    ) -> None:
        tk.Label(frame, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self._var = tk.StringVar(value=default)
        entry = ttk.Entry(frame, textvariable=self._var, show=show, width=32)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)
        tip(entry, hilfe)

    @property
    def wert(self) -> str:
        return self._var.get().strip()


# ─────────────────────────────────────────────────────────────────────────────
# Mitarbeiter-Tab
# ─────────────────────────────────────────────────────────────────────────────

class MitarbeiterView(ttk.Frame):
    """Tab: Mitarbeiterverwaltung.

    Zeigt alle Mitarbeitenden mit ID, Personalnummer, Name und Status.
    Ermöglicht Anlegen und Deaktivieren.
    """

    _COLUMNS = ("id", "personalnr", "name", "status")
    _HEADERS = {"id": "ID", "personalnr": "Pers.-Nr.", "name": "Name", "status": "Status"}
    _WIDTHS = {"id": 50, "personalnr": 100, "name": 220, "status": 80}

    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self._app = app
        self._build()

    def _build(self) -> None:
        # Toolbar
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))

        anlegen_btn = ttk.Button(bar, text="➕ Anlegen", command=self._anlegen)
        anlegen_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            anlegen_btn,
            "Neuen Mitarbeiter anlegen.\n\n"
            "Sie werden nach Personalnummer, Vor- und Nachname gefragt. "
            "Die Personalnummer muss im System eindeutig sein. "
            "Der Mitarbeiter wird sofort als aktiv gesetzt.",
        )

        deakt_btn = ttk.Button(bar, text="🚫 Deaktivieren", command=self._deaktivieren)
        deakt_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            deakt_btn,
            "Markierten Mitarbeiter deaktivieren.\n\n"
            "Deaktivierte Mitarbeitende können keine Buchungen mehr durchführen. "
            "Ihre Daten und bisherigen Buchungen bleiben vollständig erhalten. "
            "Die Deaktivierung kann nicht automatisch rückgängig gemacht werden — "
            "wenden Sie sich an die technisch verantwortliche Person.",
        )

        aktualisieren_btn = ttk.Button(bar, text="🔄 Aktualisieren", command=self.laden)
        aktualisieren_btn.pack(side=tk.LEFT)
        tip(aktualisieren_btn, "Liste neu laden.")

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self._tree = ttk.Treeview(
            tree_frame, columns=self._COLUMNS, show="headings", selectmode="browse"
        )
        for col in self._COLUMNS:
            self._tree.heading(col, text=self._HEADERS[col])
            self._tree.column(col, width=self._WIDTHS[col], minwidth=40)
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll_y.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.bind("<Double-1>", lambda _: self._detail_anzeigen())

        # Statuszeile
        self._info = tk.StringVar(value="Keine Verbindung.")
        tk.Label(self, textvariable=self._info, foreground="#555", anchor="w").pack(
            fill=tk.X, padx=8, pady=(0, 6)
        )

    def laden(self) -> None:
        self._tree.delete(*self._tree.get_children())
        if not self._app.db_path:
            self._info.set("Nicht verbunden.")
            return
        try:
            conn = open_connection(self._app.db_path)
            rows = conn.execute(
                "SELECT id, personnel_no, first_name, last_name, active "
                "FROM employees ORDER BY personnel_no"
            ).fetchall()
            conn.close()
        except Exception as exc:
            self._info.set(f"Fehler: {exc}")
            return

        aktiv = sum(1 for r in rows if r["active"])
        for r in rows:
            name = f"{r['first_name']} {r['last_name']}"
            status = "aktiv" if r["active"] else "inaktiv"
            self._tree.insert("", tk.END, iid=str(r["id"]), values=(r["id"], r["personnel_no"], name, status))
        self._info.set(f"{len(rows)} Mitarbeiter geladen ({aktiv} aktiv).")

    def _anlegen(self) -> None:
        if not self._app.user_id:
            messagebox.showwarning("Keine Benutzer-ID", "Bitte zuerst eine Benutzer-ID eingeben.", parent=self)
            return
        dlg = _MitarbeiterAnlegenDialog(self, self._app)
        self.wait_window(dlg)
        if dlg.ok:
            self.laden()

    def _deaktivieren(self) -> None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte zuerst einen Mitarbeiter auswählen.", parent=self)
            return
        emp_id = int(sel[0])
        name = self._tree.item(sel[0], "values")[2]
        if not messagebox.askyesno(
            "Deaktivieren bestätigen",
            f"Mitarbeiter «{name}» (ID {emp_id}) wirklich deaktivieren?\n\n"
            "Buchungen und Daten bleiben erhalten.\n"
            "Der Mitarbeiter kann danach keine Buchungen mehr durchführen.",
            parent=self,
        ):
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            deactivate_employee(uow, self._app.user_id, emp_id)
            _close(conn, audit_conn)
            self._app.status(f"Mitarbeiter {emp_id} deaktiviert.")
            self.laden()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)
        except Exception as exc:
            messagebox.showerror("Unerwarteter Fehler", str(exc), parent=self)

    def _detail_anzeigen(self) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        werte = self._tree.item(sel[0], "values")
        messagebox.showinfo(
            "Mitarbeiter-Details",
            f"ID: {werte[0]}\nPersonalnummer: {werte[1]}\nName: {werte[2]}\nStatus: {werte[3]}",
            parent=self,
        )


class _MitarbeiterAnlegenDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self.title("Mitarbeiter anlegen")
        self.resizable(False, False)
        self.grab_set()
        self._app = app
        self.ok = False
        self._build()

    def _build(self) -> None:
        f = ttk.LabelFrame(self, text="Mitarbeiterdaten", padding=12)
        f.pack(padx=16, pady=12, fill=tk.BOTH)
        self._nr = EingabeFeld(f, 0, "Personalnummer:", "Eindeutige Kennung (z. B. M001). Darf kein anderes aktives Konto haben.")
        self._vn = EingabeFeld(f, 1, "Vorname:", "Vorname der Mitarbeiterin / des Mitarbeiters.")
        self._nn = EingabeFeld(f, 2, "Nachname:", "Nachname der Mitarbeiterin / des Mitarbeiters.")
        f.columnconfigure(1, weight=1)

        btn_f = ttk.Frame(self)
        btn_f.pack(pady=(0, 12))
        ok_btn = ttk.Button(btn_f, text="Anlegen", command=self._ok)
        ok_btn.pack(side=tk.LEFT, padx=6)
        tip(ok_btn, "Mitarbeiter in der Datenbank anlegen und Dialog schließen.")
        ttk.Button(btn_f, text="Abbrechen", command=self.destroy).pack(side=tk.LEFT, padx=6)
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self.destroy())

    def _ok(self) -> None:
        if not self._nr.wert or not self._vn.wert or not self._nn.wert:
            messagebox.showerror("Fehler", "Alle Felder sind Pflicht.", parent=self)
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            result = create_employee(uow, self._app.user_id, self._nr.wert, self._vn.wert, self._nn.wert)
            _close(conn, audit_conn)
            self._app.status(f"Mitarbeiter angelegt (ID {result.employee_id}).")
            self.ok = True
            self.destroy()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)
        except Exception as exc:
            messagebox.showerror("Unerwarteter Fehler", str(exc), parent=self)


# ─────────────────────────────────────────────────────────────────────────────
# Karten-Tab
# ─────────────────────────────────────────────────────────────────────────────

class KartenView(ttk.Frame):
    """Tab: RFID-Kartenverwaltung."""

    _COLUMNS = ("id", "mitarbeiter_id", "uid_hash", "status", "gueltig_ab")
    _HEADERS = {"id": "ID", "mitarbeiter_id": "Mitarb.-ID", "uid_hash": "UID-Hash", "status": "Status", "gueltig_ab": "Gültig ab"}
    _WIDTHS = {"id": 50, "mitarbeiter_id": 90, "uid_hash": 220, "status": 80, "gueltig_ab": 90}

    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self._app = app
        self._build()

    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))

        zuweisen_btn = ttk.Button(bar, text="➕ Zuweisen", command=self._zuweisen)
        zuweisen_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            zuweisen_btn,
            "Neue RFID-Karte einem Mitarbeiter zuweisen.\n\n"
            "Sie benötigen die Mitarbeiter-ID (aus dem Mitarbeiter-Tab) und "
            "den SHA-256-Hash der Karte. Den Hash erhalten Sie mit dem Befehl:\n"
            "  python scripts/verify_hardware.py --numpad /dev/input/eventX --rfid /dev/input/eventY\n\n"
            "Halten Sie während des Tests die Karte an den Leser — das Script "
            "zeigt den Hash an.",
        )

        ersetzen_btn = ttk.Button(bar, text="🔄 Ersetzen", command=self._ersetzen)
        ersetzen_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            ersetzen_btn,
            "Eine verlorene oder defekte Karte durch eine neue ersetzen.\n\n"
            "Wählen Sie die alte Karte in der Liste aus und geben Sie den Hash "
            "der neuen Karte ein. Die alte Karte erhält den Status REPLACED und "
            "kann nicht mehr für Buchungen verwendet werden.",
        )

        deakt_btn = ttk.Button(bar, text="🚫 Deaktivieren", command=self._deaktivieren)
        deakt_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            deakt_btn,
            "Ausgewählte Karte deaktivieren (Status → INACTIVE).\n\n"
            "Eine deaktivierte Karte wird vom Terminal abgewiesen. "
            "Verwenden Sie diese Funktion, wenn eine Karte verloren gegangen ist "
            "und noch keine neue ausgestellt wurde.",
        )

        ttk.Button(bar, text="🔄 Aktualisieren", command=self.laden).pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._tree = ttk.Treeview(tree_frame, columns=self._COLUMNS, show="headings", selectmode="browse")
        for col in self._COLUMNS:
            self._tree.heading(col, text=self._HEADERS[col])
            self._tree.column(col, width=self._WIDTHS[col], minwidth=40)
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._info = tk.StringVar(value="Keine Verbindung.")
        tk.Label(self, textvariable=self._info, foreground="#555", anchor="w").pack(fill=tk.X, padx=8, pady=(0, 6))

    def laden(self) -> None:
        self._tree.delete(*self._tree.get_children())
        if not self._app.db_path:
            return
        try:
            conn = open_connection(self._app.db_path)
            rows = conn.execute(
                "SELECT id, employee_id, uid_hash, status, valid_from FROM rfid_cards ORDER BY id"
            ).fetchall()
            conn.close()
        except Exception as exc:
            self._info.set(f"Fehler: {exc}")
            return
        for r in rows:
            self._tree.insert("", tk.END, iid=str(r["id"]),
                values=(r["id"], r["employee_id"], r["uid_hash"][:24] + "…", r["status"], r["valid_from"]))
        self._info.set(f"{len(rows)} Karte(n) geladen.")

    def _ausgewaehlt(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte zuerst eine Karte auswählen.", parent=self)
            return None
        return int(sel[0])

    def _zuweisen(self) -> None:
        dlg = _KarteZuweisenDialog(self, self._app)
        self.wait_window(dlg)
        if dlg.ok:
            self.laden()

    def _ersetzen(self) -> None:
        karte_id = self._ausgewaehlt()
        if karte_id is None:
            return
        neuer_hash = simpledialog.askstring(
            "Karte ersetzen",
            "SHA-256-Hash der neuen Karte eingeben:\n\n"
            "(Ermitteln Sie den Hash mit scripts/verify_hardware.py)",
            parent=self,
        )
        if not neuer_hash:
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            result = replace_rfid_card(uow, self._app.user_id, karte_id, neuer_hash.strip())
            _close(conn, audit_conn)
            self._app.status(f"Karte ersetzt: alt={karte_id}, neu={result.new_card_id}.")
            self.laden()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)

    def _deaktivieren(self) -> None:
        karte_id = self._ausgewaehlt()
        if karte_id is None:
            return
        if not messagebox.askyesno("Bestätigen", f"Karte {karte_id} wirklich deaktivieren?", parent=self):
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            deactivate_rfid_card(uow, self._app.user_id, karte_id)
            _close(conn, audit_conn)
            self._app.status(f"Karte {karte_id} deaktiviert.")
            self.laden()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)


class _KarteZuweisenDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self.title("RFID-Karte zuweisen")
        self.resizable(False, False)
        self.grab_set()
        self._app = app
        self.ok = False
        self._build()

    def _build(self) -> None:
        f = ttk.LabelFrame(self, text="Kartendaten", padding=12)
        f.pack(padx=16, pady=12, fill=tk.BOTH)
        self._empid = EingabeFeld(f, 0, "Mitarbeiter-ID:", "Numerische ID des Mitarbeiters (aus dem Mitarbeiter-Tab).")
        self._hash = EingabeFeld(
            f, 1, "UID-Hash:",
            "SHA-256-Hash der RFID-Karte, wie in der Datenbank gespeichert.\n\n"
            "Führen Sie scripts/verify_hardware.py aus und scannen Sie die Karte — "
            "das Script zeigt den Hash unter 'SHA-256-Hash' an.",
        )
        f.columnconfigure(1, weight=1)
        btn_f = ttk.Frame(self)
        btn_f.pack(pady=(0, 12))
        ttk.Button(btn_f, text="Zuweisen", command=self._ok).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_f, text="Abbrechen", command=self.destroy).pack(side=tk.LEFT, padx=6)
        self.bind("<Return>", lambda _: self._ok())

    def _ok(self) -> None:
        try:
            emp_id = int(self._empid.wert)
        except ValueError:
            messagebox.showerror("Fehler", "Mitarbeiter-ID muss eine ganze Zahl sein.", parent=self)
            return
        if not self._hash.wert:
            messagebox.showerror("Fehler", "UID-Hash darf nicht leer sein.", parent=self)
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            result = assign_rfid_card(uow, self._app.user_id, emp_id, self._hash.wert)
            _close(conn, audit_conn)
            self._app.status(f"Karte zugewiesen (ID {result.card_id}).")
            self.ok = True
            self.destroy()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)


# ─────────────────────────────────────────────────────────────────────────────
# Benutzer-Tab
# ─────────────────────────────────────────────────────────────────────────────

class BenutzerView(ttk.Frame):
    """Tab: Benutzerkontenverwaltung (ADMIN, REVIEWER, TECH)."""

    _COLUMNS = ("id", "benutzername", "rolle", "status")
    _HEADERS = {"id": "ID", "benutzername": "Benutzername", "rolle": "Rolle", "status": "Status"}
    _WIDTHS = {"id": 50, "benutzername": 160, "rolle": 100, "status": 80}

    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self._app = app
        self._build()

    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))

        anlegen_btn = ttk.Button(bar, text="➕ Konto anlegen", command=self._anlegen)
        anlegen_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            anlegen_btn,
            "Neues Benutzerkonto anlegen.\n\n"
            "Erlaubte Rollen:\n"
            "  ADMIN    – Vollzugriff auf alle Verwaltungsfunktionen\n"
            "  REVIEWER – Darf Berichte einsehen und Nachträge bearbeiten\n"
            "  TECH     – Darf Systemcheck und Backup auslösen\n\n"
            "Das Passwort wird mit PBKDF2-HMAC-SHA256 gehasht gespeichert. "
            "Wird kein Passwort angegeben, wird automatisch ein sicheres Passwort "
            "generiert und einmalig angezeigt.",
        )

        bootstrap_btn = ttk.Button(bar, text="🔑 Bootstrap", command=self._bootstrap)
        bootstrap_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            bootstrap_btn,
            "Erstes Administratorkonto anlegen (Bootstrap).\n\n"
            "Diese Funktion ist nur nutzbar, solange noch kein aktives "
            "Administratorkonto existiert. Danach ist sie gesperrt.\n\n"
            "Notieren Sie das angezeigte Passwort sofort an einem sicheren Ort — "
            "es kann nicht erneut angezeigt werden.",
        )

        deakt_btn = ttk.Button(bar, text="🚫 Deaktivieren", command=self._deaktivieren)
        deakt_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(deakt_btn, "Ausgewähltes Benutzerkonto deaktivieren. Der Benutzer kann sich danach nicht mehr anmelden.")

        reakt_btn = ttk.Button(bar, text="✅ Reaktivieren", command=self._reaktivieren)
        reakt_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(reakt_btn, "Deaktiviertes Benutzerkonto wieder aktivieren.")

        rolle_btn = ttk.Button(bar, text="🔀 Rolle ändern", command=self._rolle_aendern)
        rolle_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(rolle_btn, "Rolle des ausgewählten Benutzerkontos ändern (ADMIN / REVIEWER / TECH).")

        ttk.Button(bar, text="🔄 Aktualisieren", command=self.laden).pack(side=tk.LEFT)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._tree = ttk.Treeview(tree_frame, columns=self._COLUMNS, show="headings", selectmode="browse")
        for col in self._COLUMNS:
            self._tree.heading(col, text=self._HEADERS[col])
            self._tree.column(col, width=self._WIDTHS[col], minwidth=40)
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._info = tk.StringVar(value="Keine Verbindung.")
        tk.Label(self, textvariable=self._info, foreground="#555", anchor="w").pack(fill=tk.X, padx=8, pady=(0, 6))

    def laden(self) -> None:
        self._tree.delete(*self._tree.get_children())
        if not self._app.db_path:
            return
        try:
            conn = open_connection(self._app.db_path)
            rows = conn.execute(
                "SELECT id, username, role, active FROM user_accounts "
                "WHERE role != 'EMPLOYEE' ORDER BY role, username"
            ).fetchall()
            conn.close()
        except Exception as exc:
            self._info.set(f"Fehler: {exc}")
            return
        for r in rows:
            status = "aktiv" if r["active"] else "inaktiv"
            self._tree.insert("", tk.END, iid=str(r["id"]), values=(r["id"], r["username"], r["role"], status))
        self._info.set(f"{len(rows)} Benutzerkonto/-konten geladen.")

    def _ausgewaehlt(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte zuerst ein Benutzerkonto auswählen.", parent=self)
            return None
        return int(sel[0])

    def _anlegen(self) -> None:
        dlg = _BenutzerAnlegenDialog(self, self._app)
        self.wait_window(dlg)
        if dlg.ok:
            self.laden()

    def _bootstrap(self) -> None:
        benutzername = simpledialog.askstring("Bootstrap", "Benutzername des ersten Administrators:", parent=self)
        if not benutzername:
            return
        passwort = simpledialog.askstring(
            "Bootstrap",
            "Passwort (leer lassen für automatisch generiertes Passwort):",
            parent=self,
            show="*",
        )
        plain = passwort if passwort else secrets.token_urlsafe(12)
        pw_hash = _hash_password(plain)
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            result = bootstrap_admin(uow, benutzername, pw_hash)
            _close(conn, audit_conn)
            msg = f"Erstes Administratorkonto angelegt (ID {result.user_id})."
            if not passwort:
                msg += f"\n\nGeneriertes Passwort (einmalig sichtbar):\n{plain}\n\nNotieren Sie es sofort!"
            messagebox.showinfo("Bootstrap erfolgreich", msg, parent=self)
            self._app.status("Bootstrap abgeschlossen.")
            self.laden()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)

    def _deaktivieren(self) -> None:
        uid = self._ausgewaehlt()
        if uid is None:
            return
        if not self._app.user_id:
            messagebox.showwarning("Keine Benutzer-ID", "Benutzer-ID fehlt.", parent=self)
            return
        if not messagebox.askyesno("Bestätigen", f"Benutzerkonto {uid} deaktivieren?", parent=self):
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            deactivate_user_account(uow, self._app.user_id, uid)
            _close(conn, audit_conn)
            self._app.status(f"Benutzerkonto {uid} deaktiviert.")
            self.laden()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)

    def _reaktivieren(self) -> None:
        uid = self._ausgewaehlt()
        if uid is None:
            return
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            reactivate_user_account(uow, self._app.user_id, uid)
            _close(conn, audit_conn)
            self._app.status(f"Benutzerkonto {uid} reaktiviert.")
            self.laden()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)

    def _rolle_aendern(self) -> None:
        uid = self._ausgewaehlt()
        if uid is None:
            return
        dlg = _RolleAendernDialog(self, self._app, uid)
        self.wait_window(dlg)
        if dlg.ok:
            self.laden()


class _BenutzerAnlegenDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self.title("Benutzerkonto anlegen")
        self.resizable(False, False)
        self.grab_set()
        self._app = app
        self.ok = False
        self._build()

    def _build(self) -> None:
        f = ttk.LabelFrame(self, text="Kontodaten", padding=12)
        f.pack(padx=16, pady=12, fill=tk.BOTH)
        self._name = EingabeFeld(f, 0, "Benutzername:", "Eindeutiger Anmeldename (ohne Leerzeichen).")
        self._pw = EingabeFeld(f, 1, "Passwort:", "Passwort (leer lassen für automatisch generierten Wert).", show="*")

        tk.Label(f, text="Rolle:", anchor="w").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self._rolle_var = tk.StringVar(value="REVIEWER")
        rolle_cb = ttk.Combobox(f, textvariable=self._rolle_var, values=["ADMIN", "REVIEWER", "TECH"], state="readonly", width=12)
        rolle_cb.grid(row=2, column=1, sticky="w", padx=(0, 8), pady=4)
        tip(rolle_cb, "ADMIN: Vollzugriff | REVIEWER: Berichte und Nachträge | TECH: Systemcheck und Backup")

        tk.Label(f, text="Mitarbeiter-ID:", anchor="w").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self._empid_var = tk.StringVar(value="")
        empid_e = ttk.Entry(f, textvariable=self._empid_var, width=10)
        empid_e.grid(row=3, column=1, sticky="w", padx=(0, 8), pady=4)
        tip(empid_e, "Optional: ID des verknüpften Mitarbeiters. Kann leer bleiben.")

        f.columnconfigure(1, weight=1)
        btn_f = ttk.Frame(self)
        btn_f.pack(pady=(0, 12))
        ttk.Button(btn_f, text="Anlegen", command=self._ok).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_f, text="Abbrechen", command=self.destroy).pack(side=tk.LEFT, padx=6)

    def _ok(self) -> None:
        if not self._name.wert:
            messagebox.showerror("Fehler", "Benutzername darf nicht leer sein.", parent=self)
            return
        plain = self._pw.wert or secrets.token_urlsafe(12)
        pw_hash = _hash_password(plain)
        emp_id_str = self._empid_var.get().strip()
        emp_id = None
        if emp_id_str:
            try:
                emp_id = int(emp_id_str)
            except ValueError:
                messagebox.showerror("Fehler", "Mitarbeiter-ID muss eine Zahl sein.", parent=self)
                return
        try:
            rolle = UserRole(self._rolle_var.get())
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            result = create_user_account(uow, self._app.user_id, self._name.wert, pw_hash, rolle, emp_id)
            _close(conn, audit_conn)
            msg = f"Benutzerkonto angelegt (ID {result.user_id})."
            if not self._pw.wert:
                msg += f"\n\nGeneriertes Passwort (einmalig sichtbar):\n{plain}\n\nNotieren Sie es sofort!"
            messagebox.showinfo("Erfolg", msg, parent=self)
            self._app.status(f"Benutzerkonto {result.user_id} angelegt.")
            self.ok = True
            self.destroy()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)


class _RolleAendernDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp", target_id: int) -> None:
        super().__init__(parent)
        self.title("Rolle ändern")
        self.resizable(False, False)
        self.grab_set()
        self._app = app
        self._target_id = target_id
        self.ok = False
        self._build()

    def _build(self) -> None:
        f = ttk.Frame(self)
        f.pack(padx=16, pady=16)
        tk.Label(f, text=f"Neue Rolle für Benutzerkonto {self._target_id}:", anchor="w").grid(row=0, column=0, padx=(0, 8), pady=4)
        self._var = tk.StringVar(value="REVIEWER")
        cb = ttk.Combobox(f, textvariable=self._var, values=["ADMIN", "REVIEWER", "TECH"], state="readonly", width=12)
        cb.grid(row=0, column=1, pady=4)
        tip(cb, "Neue Rolle auswählen. EMPLOYEE-Rolle ist nicht erlaubt.")
        btn_f = ttk.Frame(self)
        btn_f.pack(pady=(0, 12))
        ttk.Button(btn_f, text="Ändern", command=self._ok).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_f, text="Abbrechen", command=self.destroy).pack(side=tk.LEFT, padx=6)

    def _ok(self) -> None:
        try:
            uow, conn, audit_conn = _make_uow(self._app.db_path)
            change_user_role(uow, self._app.user_id, self._target_id, UserRole(self._var.get()))
            _close(conn, audit_conn)
            self._app.status(f"Rolle von Konto {self._target_id} geändert.")
            self.ok = True
            self.destroy()
        except DomainError as exc:
            messagebox.showerror("Fehler", exc.message, parent=self)


# ─────────────────────────────────────────────────────────────────────────────
# System-Tab
# ─────────────────────────────────────────────────────────────────────────────

class SystemView(ttk.Frame):
    """Tab: Systemcheck und Backup."""

    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self._app = app
        self._build()

    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))

        check_btn = ttk.Button(bar, text="🔍 Systemcheck", command=self._systemcheck)
        check_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            check_btn,
            "Systemcheck durchführen (db_access, config_keys, nas_reachability, "
            "fk_consistency, ntp_sync, device_availability).\n\n"
            "Das Ergebnis wird in der Liste darunter angezeigt und in der Datenbank "
            "unter system_events protokolliert (SELFTEST_OK / SELFTEST_FAIL).",
        )

        backup_btn = ttk.Button(bar, text="💾 Backup", command=self._backup)
        backup_btn.pack(side=tk.LEFT, padx=(0, 4))
        tip(
            backup_btn,
            "Manuelles Datenbankbackup erstellen.\n\n"
            "Das Backup wird im konfigurierten Backup-Verzeichnis "
            "(backup.backup_dir in system_config) gespeichert. "
            "Ist NAS-Synchronisation aktiv (backup.nas_enabled=true), "
            "wird das Backup anschließend auf den NAS-Pfad übertragen.\n\n"
            "Das lokale Backup gelingt auch ohne NAS. Ein NAS-Fehler wird "
            "als Fehler gemeldet und der Prozess endet mit Exit 1.",
        )

        # Ergebnisbereich
        result_frame = ttk.LabelFrame(self, text="Systemcheck-Ergebnis", padding=8)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        columns = ("bereich", "status", "detail")
        self._tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
        self._tree.heading("bereich", text="Prüfbereich")
        self._tree.heading("status", text="Status")
        self._tree.heading("detail", text="Detail")
        self._tree.column("bereich", width=160, minwidth=100)
        self._tree.column("status", width=60, minwidth=50)
        self._tree.column("detail", width=400, minwidth=200)
        scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._gesamt = tk.StringVar(value="Noch kein Systemcheck durchgeführt.")
        tk.Label(self, textvariable=self._gesamt, anchor="w", font=("TkDefaultFont", 0, "bold")).pack(
            fill=tk.X, padx=8, pady=(0, 8)
        )

    def _systemcheck(self) -> None:
        if not self._app.db_path:
            messagebox.showwarning("Nicht verbunden", "Bitte zuerst eine Datenbank öffnen.", parent=self)
            return
        self._tree.delete(*self._tree.get_children())
        self._gesamt.set("Systemcheck läuft …")
        self.update()
        try:
            result = run_system_check(self._app.db_path)
        except Exception as exc:
            self._gesamt.set(f"Fehler beim Systemcheck: {exc}")
            return

        for check in result.checks:
            status_text = "OK" if check.ok else "FEHLER"
            tag = "ok" if check.ok else "fail"
            self._tree.insert("", tk.END, values=(check.name, status_text, check.detail), tags=(tag,))

        self._tree.tag_configure("ok", foreground="#2e7d32")
        self._tree.tag_configure("fail", foreground="#c62828")

        gesamt_text = "✅ Systemcheck bestanden." if result.overall_ok else "❌ Systemcheck: FEHLER aufgetreten."
        self._gesamt.set(gesamt_text)
        self._app.status(gesamt_text)

    def _backup(self) -> None:
        if not self._app.db_path:
            messagebox.showwarning("Nicht verbunden", "Bitte zuerst eine Datenbank öffnen.", parent=self)
            return
        try:
            conn = open_connection(self._app.db_path)
            row = conn.execute(
                "SELECT config_value_json FROM system_config "
                "WHERE config_key = 'backup.backup_dir' ORDER BY version DESC LIMIT 1"
            ).fetchone()
            conn.close()
        except Exception as exc:
            messagebox.showerror("Fehler", str(exc), parent=self)
            return

        if row is None:
            messagebox.showerror(
                "Konfiguration fehlt",
                "backup.backup_dir ist nicht konfiguriert.\n"
                "Bitte zuerst scripts/setup.py ausführen.",
                parent=self,
            )
            return

        backup_dir = Path(json.loads(row["config_value_json"]))
        self._app.status("Backup läuft …")
        self.update()
        try:
            service = SQLiteBackupService(self._app.db_path, backup_dir)
            backup_path = service.create_local_backup()
            msg = f"Backup erstellt:\n{backup_path}"
            self._app.status(f"Backup erstellt: {backup_path.name}")
            messagebox.showinfo("Backup erfolgreich", msg, parent=self)
        except Exception as exc:
            messagebox.showerror("Backup fehlgeschlagen", str(exc), parent=self)
            self._app.status("Backup fehlgeschlagen.")


# ─────────────────────────────────────────────────────────────────────────────
# Regelzeiten-Tab (Lesend)
# ─────────────────────────────────────────────────────────────────────────────

class RegelzeitenView(ttk.Frame):
    """Tab: Aktive Regelarbeitszeiten anzeigen."""

    _COLUMNS = ("id", "scope", "mitarb", "tag", "von", "bis", "gueltig_ab")
    _HEADERS = {"id": "ID", "scope": "Scope", "mitarb": "Mitarb.-ID", "tag": "Tag", "von": "Von", "bis": "Bis", "gueltig_ab": "Gültig ab"}
    _WIDTHS = {"id": 45, "scope": 80, "mitarb": 80, "tag": 45, "von": 60, "bis": 60, "gueltig_ab": 90}
    _TAGE = {1: "Mo", 2: "Di", 3: "Mi", 4: "Do", 5: "Fr", 6: "Sa", 7: "So"}

    def __init__(self, parent: tk.Widget, app: "ArbeitszeitApp") -> None:
        super().__init__(parent)
        self._app = app
        self._build()

    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=8, pady=(8, 4))
        ttk.Button(bar, text="🔄 Aktualisieren", command=self.laden).pack(side=tk.LEFT, padx=(0, 4))

        hinweis = tk.Label(
            bar,
            text="Regelzeiten setzen: Admin-CLI → schedule set",
            foreground="#555",
        )
        hinweis.pack(side=tk.LEFT, padx=12)
        tip(
            hinweis,
            "Regelarbeitszeiten können über die Admin-CLI geändert werden:\n\n"
            "  python -m arbeitszeit.presentation.admin_cli.main \\\n"
            "    --db <DB> --user-id <ID> schedule set \\\n"
            "    --weekday 1 --start 07:30 --end 18:00 --from 2026-08-01\n\n"
            "Mit optionalem --employee-id für mitarbeiterspezifische Ausnahmen.",
        )

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._tree = ttk.Treeview(tree_frame, columns=self._COLUMNS, show="headings", selectmode="browse")
        for col in self._COLUMNS:
            self._tree.heading(col, text=self._HEADERS[col])
            self._tree.column(col, width=self._WIDTHS[col], minwidth=40)
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._info = tk.StringVar(value="Keine Verbindung.")
        tk.Label(self, textvariable=self._info, foreground="#555", anchor="w").pack(fill=tk.X, padx=8, pady=(0, 6))

    def laden(self) -> None:
        self._tree.delete(*self._tree.get_children())
        if not self._app.db_path:
            return
        try:
            conn = open_connection(self._app.db_path)
            rows = conn.execute(
                "SELECT id, scope_type, scope_employee_id, weekday, start_time, end_time, valid_from "
                "FROM work_schedule_versions WHERE valid_until IS NULL ORDER BY scope_type, weekday"
            ).fetchall()
            conn.close()
        except Exception as exc:
            self._info.set(f"Fehler: {exc}")
            return
        for r in rows:
            tag = self._TAGE.get(r["weekday"], str(r["weekday"]))
            self._tree.insert("", tk.END, values=(
                r["id"], r["scope_type"], r["scope_employee_id"] or "—",
                tag, r["start_time"], r["end_time"], r["valid_from"]
            ))
        self._info.set(f"{len(rows)} aktive Version(en).")


# ─────────────────────────────────────────────────────────────────────────────
# Hauptanwendung
# ─────────────────────────────────────────────────────────────────────────────

class ArbeitszeitApp(tk.Tk):
    """Hauptfenster der Arbeitszeit-Verwaltungs-GUI."""

    def __init__(self, db_path: Path | None = None, user_id: int | None = None) -> None:
        super().__init__()
        self.db_path = db_path
        self.user_id = user_id
        self.title("Arbeitszeit — Verwaltung")
        self.minsize(760, 500)
        self.geometry("960x620")
        self._build_ui()
        self._build_menu()
        if not self.db_path:
            self.after(100, self._verbindung_herstellen)

    def _build_ui(self) -> None:
        # Kopfzeile
        header = tk.Frame(self, background="#1e3a6e")
        header.pack(fill=tk.X)
        tk.Label(
            header, text="Arbeitszeit — Verwaltung", font=("TkHeadingFont", 13, "bold"),
            background="#1e3a6e", foreground="white", padx=12, pady=6,
        ).pack(side=tk.LEFT)

        self._conn_label = tk.Label(
            header, text="Nicht verbunden", foreground="#aaa",
            background="#1e3a6e", padx=12,
        )
        self._conn_label.pack(side=tk.RIGHT)

        # Notebook (Tabs)
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._view_mitarbeiter = MitarbeiterView(self._nb, self)
        self._view_karten = KartenView(self._nb, self)
        self._view_benutzer = BenutzerView(self._nb, self)
        self._view_regelzeiten = RegelzeitenView(self._nb, self)
        self._view_system = SystemView(self._nb, self)

        self._nb.add(self._view_mitarbeiter, text="👥 Mitarbeiter")
        self._nb.add(self._view_karten, text="💳 Karten")
        self._nb.add(self._view_benutzer, text="👤 Benutzer")
        self._nb.add(self._view_regelzeiten, text="📅 Regelzeiten")
        self._nb.add(self._view_system, text="⚙ System")
        self._nb.bind("<<NotebookTabChanged>>", self._tab_gewechselt)

        # Statusleiste
        self._status_var = tk.StringVar(value="Bereit.")
        statusbar = tk.Label(
            self, textvariable=self._status_var,
            relief=tk.SUNKEN, anchor="w", padx=8, pady=3,
            background="#f5f5f5",
        )
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        # Datei
        datei_menu = tk.Menu(menubar, tearoff=False)
        datei_menu.add_command(
            label="Verbindung herstellen …", accelerator="Ctrl+O",
            command=self._verbindung_herstellen,
        )
        datei_menu.add_separator()
        datei_menu.add_command(label="Beenden", accelerator="Ctrl+Q", command=self.quit)
        menubar.add_cascade(label="Datei", menu=datei_menu)

        # Ansicht
        ansicht_menu = tk.Menu(menubar, tearoff=False)
        ansicht_menu.add_command(label="Alles neu laden", accelerator="F5", command=self._alle_laden)
        menubar.add_cascade(label="Ansicht", menu=ansicht_menu)

        # Hilfe
        hilfe_menu = tk.Menu(menubar, tearoff=False)
        hilfe_menu.add_command(label="Kurzanleitung", accelerator="F1", command=self._hilfe_kurzanleitung)
        hilfe_menu.add_command(label="Tastenkürzel", command=self._hilfe_tastaturkuerzel)
        hilfe_menu.add_separator()
        hilfe_menu.add_command(label="Über Arbeitszeit", command=self._ueber)
        menubar.add_cascade(label="Hilfe", menu=hilfe_menu)

        self.configure(menu=menubar)

        # Tastenkürzel
        self.bind("<Control-o>", lambda _: self._verbindung_herstellen())
        self.bind("<Control-q>", lambda _: self.quit())
        self.bind("<F5>", lambda _: self._alle_laden())
        self.bind("<F1>", lambda _: self._hilfe_kurzanleitung())

    def _tab_gewechselt(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        tab = self._nb.select()
        view = self._nb.nametowidget(tab)
        if hasattr(view, "laden") and self.db_path:
            view.laden()

    def _verbindung_herstellen(self) -> None:
        dlg = VerbindungsDialog(self)
        self.wait_window(dlg)
        if dlg.db_path:
            self.db_path = dlg.db_path
            self.user_id = dlg.user_id
            self._conn_label.configure(
                text=f"📂 {dlg.db_path.name}  |  Benutzer-ID: {dlg.user_id or '—'}",
                foreground="#90caf9",
            )
            self.status(f"Verbunden mit {dlg.db_path.name}.")
            self._alle_laden()

    def _alle_laden(self) -> None:
        for view in (
            self._view_mitarbeiter, self._view_karten, self._view_benutzer,
            self._view_regelzeiten,
        ):
            view.laden()

    def status(self, text: str) -> None:
        self._status_var.set(text)
        self.update_idletasks()

    def _hilfe_kurzanleitung(self) -> None:
        inhalt = (
            "ARBEITSZEIT — VERWALTUNGS-GUI\n"
            "════════════════════════════\n\n"
            "Diese Oberfläche ermöglicht die Verwaltung des Zeiterfassungssystems "
            "ohne Kommandozeile.\n\n"
            "ERSTE SCHRITTE\n"
            "──────────────\n"
            "1. Datei → Verbindung herstellen (Strg+O)\n"
            "   Wählen Sie die Datenbankdatei (arbeitszeit.db) und Ihre Benutzer-ID.\n\n"
            "2. ERSTMALIGE EINRICHTUNG (Bootstrap)\n"
            "   Wenn noch kein Administrator existiert:\n"
            "   → Tab «Benutzer» → Schaltfläche «Bootstrap»\n"
            "   → Benutzernamen eingeben → Passwort notieren!\n\n"
            "TABS\n"
            "────\n"
            "👥 Mitarbeiter  Mitarbeitende anlegen und deaktivieren\n"
            "💳 Karten       RFID-Karten zuweisen, ersetzen, deaktivieren\n"
            "👤 Benutzer     Admin-/Reviewer-/Tech-Konten verwalten\n"
            "📅 Regelzeiten  Aktive Arbeitszeiten anzeigen (Änderung über CLI)\n"
            "⚙ System       Systemcheck und Backup\n\n"
            "HINWEISE\n"
            "────────\n"
            "• Alle Listen können mit «Aktualisieren» (F5) neu geladen werden.\n"
            "• Alle Schaltflächen haben Tooltips — kurz mit der Maus darüber "
            "verweilen.\n"
            "• Passwörter werden niemals im Klartext gespeichert.\n"
            "• Buchungen und Berichte: Admin-CLI oder befehlsreferenz_arbeitszeit.md\n\n"
            "Bei Fragen: handbuch_arbeitszeit.md lesen."
        )
        HilfeDialog(self, "Kurzanleitung", inhalt)

    def _hilfe_tastaturkuerzel(self) -> None:
        inhalt = (
            "TASTENKÜRZEL\n"
            "════════════\n\n"
            "Strg+O    Verbindung herstellen\n"
            "F5        Alle Listen neu laden\n"
            "F1        Kurzanleitung öffnen\n"
            "Strg+Q    Anwendung beenden\n\n"
            "In Dialogen:\n"
            "Enter     Bestätigen\n"
            "Escape    Abbrechen\n"
        )
        HilfeDialog(self, "Tastenkürzel", inhalt)

    def _ueber(self) -> None:
        messagebox.showinfo(
            "Über Arbeitszeit",
            "arbeitszeit — Lokales Zeiterfassungssystem\n"
            "Zahnarztpraxis\n\n"
            "Admin-GUI v1.0 (tkinter/ttk)\n\n"
            "Dokumentation:\n"
            "  handbuch_arbeitszeit.md\n"
            "  befehlsreferenz_arbeitszeit.md",
            parent=self,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Einstiegspunkt
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Arbeitszeit — grafische Verwaltungsoberfläche",
        epilog="Ohne Argumente erscheint ein Verbindungsdialog beim Start.",
    )
    parser.add_argument("--db", type=Path, default=None, metavar="PFAD",
                        help="Pfad zur SQLite-Datenbankdatei")
    parser.add_argument("--user-id", type=int, default=None, metavar="ID",
                        help="Benutzer-ID (alternativ: ADMIN_USER_ID-Umgebungsvariable)")
    args = parser.parse_args()

    user_id = args.user_id
    if user_id is None:
        env_val = os.environ.get("ADMIN_USER_ID")
        if env_val:
            try:
                user_id = int(env_val)
            except ValueError:
                pass

    app = ArbeitszeitApp(db_path=args.db, user_id=user_id)
    app.mainloop()


if __name__ == "__main__":
    import argparse
    main()
else:
    import argparse
