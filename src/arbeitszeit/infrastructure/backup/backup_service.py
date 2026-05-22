import json
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from arbeitszeit.domain.entities import AuditLogEntry
from arbeitszeit.infrastructure.db.connection import open_connection
from arbeitszeit.infrastructure.db.repositories import SQLiteAuditLogRepository


@dataclass(frozen=True)
class BackupResult:
    backup_path: Path
    size_bytes: int
    synced_to_nas: bool


class SQLiteBackupService:
    def __init__(self, db_path: Path, backup_dir: Path) -> None:
        self._db_path = db_path
        self._backup_dir = backup_dir

    def create_local_backup(self, *, now: datetime | None = None) -> Path:
        """Online-Backup via SQLite-Backup-API. DB bleibt während des Backups lesbar/schreibbar."""
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        if now is None:
            now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%dT%H%M%SZ")
        backup_path = self._backup_dir / f"arbeitszeit_{timestamp}.db"
        src = sqlite3.connect(str(self._db_path))
        try:
            dst = sqlite3.connect(str(backup_path))
            try:
                src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()
        self._log_audit(
            "BACKUP_CREATED",
            {"backup_path": str(backup_path), "size_bytes": backup_path.stat().st_size},
        )
        return backup_path

    def sync_to_nas(self, nas_path: Path) -> None:
        """Synchronisiert backup_dir → NAS via rsync. Wirft CalledProcessError bei Fehler."""
        try:
            subprocess.run(
                [
                    "rsync",
                    "--archive",
                    "--delete",
                    f"{self._backup_dir}/",
                    f"{nas_path}/",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            self._log_audit(
                "BACKUP_SYNC_FAILED",
                {"nas_path": str(nas_path), "returncode": exc.returncode},
            )
            raise
        self._log_audit("BACKUP_SYNCED_TO_NAS", {"nas_path": str(nas_path)})

    def restore_from(self, backup_path: Path) -> None:
        """Stellt die Datenbank aus einer Backup-Datei wieder her.

        Vorbedingung: Keine offenen Verbindungen zur Ziel-DB beim Aufruf.
        Führt nach dem Restore PRAGMA integrity_check aus.
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup-Datei nicht gefunden: {backup_path}")
        src = sqlite3.connect(str(backup_path))
        try:
            dst = sqlite3.connect(str(self._db_path))
            try:
                src.backup(dst)
                result = dst.execute("PRAGMA integrity_check").fetchone()[0]
                if result != "ok":
                    raise RuntimeError(
                        f"Integritätsprüfung der wiederhergestellten DB fehlgeschlagen: {result}"
                    )
            finally:
                dst.close()
        finally:
            src.close()
        # Eintrag landet in der gerade wiederhergestellten DB — das ist gewollt:
        # RESTORE_COMPLETED ist ein nachgelagertes Betriebsereignis im neuen Ist-Zustand,
        # kein Teil des gesicherten Stands.
        self._log_audit(
            "RESTORE_COMPLETED",
            {
                "backup_path": str(backup_path),
                "backup_mtime": backup_path.stat().st_mtime,
            },
        )

    def run(self, *, nas_path: Path | None = None) -> BackupResult:
        """Erstellt lokales Backup und synchronisiert optional zum NAS."""
        backup_path = self.create_local_backup()
        synced = False
        if nas_path is not None:
            self.sync_to_nas(nas_path)
            synced = True
        return BackupResult(
            backup_path=backup_path,
            size_bytes=backup_path.stat().st_size,
            synced_to_nas=synced,
        )

    def _log_audit(self, event_type: str, details: dict) -> None:
        conn = open_connection(self._db_path)
        try:
            repo = SQLiteAuditLogRepository(conn)
            repo.add(AuditLogEntry(
                id=0,
                event_type=event_type,
                object_type="BACKUP",
                object_id=0,
                user_id=None,
                employee_id=None,
                event_at=datetime.now(timezone.utc),
                details_json=json.dumps(details, default=str),
            ))
        finally:
            conn.close()
