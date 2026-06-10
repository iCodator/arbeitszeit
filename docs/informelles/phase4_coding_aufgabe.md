# Programmieraufgabe: `restore_from()` um optionalen Export-Restore ergänzen

## Herleitung aus `phase4_planung.md`

Das Dokument beschreibt den Backup-Service in Schritt 7 und vermerkt explizit:

> „Eine spätere Erweiterung von `restore_from()` um einen optionalen
> Export-Restore-Parameter ist fachlich sinnvoll, ist aber **kein Pflichtinhalt
> von Schritt 7**."

Diese Erweiterung ist jetzt fällig, weil die Lücke betrieblich relevant ist:

### Asymmetrie zwischen Backup und Restore

**Backup** (`create_local_backup()`) — bereits vollständig implementiert:

```python
# backup_service.py:54–57
if self._export_dir is not None and self._export_dir.exists():
    shutil.copytree(
        self._export_dir,
        self._backup_dir / "exports",   # ← Exportdateien landen im Backup
        ...
    )
```

Tests in `test_backup.py:280–291` verifizieren: Backup enthält `exports/bericht.csv`
und `exports/bericht.pdf`.

**Restore** (`restore_from()`) — aktuell nur DB:

```python
# backup_service.py:97–128 — nur SQLite-DB, keine Exportdateien
src.backup(dst)
```

Konsequenz: Nach einem Restore stehen die exportierten CSV/PDF-Berichte nicht
mehr im Exportverzeichnis zur Verfügung, obwohl sie im Backup vorhanden sind.
Ein Praxisnutzer, der einen Restore durchführt, verliert Exportdateien stille.

---

## Aufgabe

**`restore_from()` um `restore_exports`-Parameter ergänzen und mit einem
E2E-Test absichern.**

### 1. `backup_service.py`: `restore_from()` erweitern

Vorher:

```python
def restore_from(self, backup_path: Path) -> None:
    """Stellt die Datenbank aus einer Backup-Datei wieder her."""
    if not backup_path.exists():
        raise FileNotFoundError(...)
    src = sqlite3.connect(str(backup_path))
    try:
        dst = sqlite3.connect(str(self._db_path))
        try:
            src.backup(dst)
            ...
```

Nachher:

```python
def restore_from(self, backup_path: Path, *, restore_exports: bool = False) -> None:
    """Stellt die Datenbank aus einer Backup-Datei wieder her.

    restore_exports: Falls True und self._export_dir gesetzt, werden
    Exportdateien aus <backup_dir>/exports/ zurück in self._export_dir
    kopiert (vorhandene Dateien werden überschrieben, neue hinzugefügt).
    Hat keinen Effekt, wenn self._export_dir nicht gesetzt oder
    <backup_dir>/exports/ nicht existiert.
    """
    if not backup_path.exists():
        raise FileNotFoundError(...)
    src = sqlite3.connect(str(backup_path))
    try:
        dst = sqlite3.connect(str(self._db_path))
        try:
            src.backup(dst)
            ...
        finally:
            dst.close()
    finally:
        src.close()

    if restore_exports and self._export_dir is not None:
        exports_in_backup = backup_path.parent / "exports"
        if exports_in_backup.exists():
            shutil.copytree(
                exports_in_backup,
                self._export_dir,
                dirs_exist_ok=True,
            )

    self._log_audit(...)
```

**Wichtig:** `restore_exports=False` ist der Default — keine bestehenden Aufrufer
brechen. `admin system backup` und `scripts/backup.py` bleiben unverändert.

### 2. `tests/e2e/test_backup.py`: Drei neue Tests

```python
def test_restore_with_exports_kopiert_exportdateien_zurueck(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    (export_dir / "bericht.csv").write_text("inhalt")

    service = SQLiteBackupService(db, tmp_path / "backups", export_dir=export_dir)
    _make_db(db)
    backup_path = service.create_local_backup()

    # Exportdatei nach Backup löschen
    (export_dir / "bericht.csv").unlink()
    assert not (export_dir / "bericht.csv").exists()

    service.restore_from(backup_path, restore_exports=True)
    assert (export_dir / "bericht.csv").exists()


def test_restore_ohne_flag_stellt_keine_exporte_wieder_her(tmp_path):
    db = tmp_path / "arbeitszeit.db"
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    (export_dir / "bericht.csv").write_text("inhalt")

    service = SQLiteBackupService(db, tmp_path / "backups", export_dir=export_dir)
    _make_db(db)
    backup_path = service.create_local_backup()

    (export_dir / "bericht.csv").unlink()
    service.restore_from(backup_path)  # restore_exports=False (Default)
    assert not (export_dir / "bericht.csv").exists()


def test_restore_with_exports_ohne_export_dir_kein_fehler(tmp_path):
    # Service ohne export_dir — restore_exports=True darf keinen Fehler werfen
    db = tmp_path / "arbeitszeit.db"
    service = SQLiteBackupService(db, tmp_path / "backups")
    _make_db(db)
    backup_path = service.create_local_backup()
    service.restore_from(backup_path, restore_exports=True)  # kein Fehler
```

---

## Betroffene Dateien

| Datei | Änderung |
|---|---|
| `src/arbeitszeit/infrastructure/backup/backup_service.py` | `restore_from()` um `restore_exports: bool = False` Parameter + `shutil.copytree`-Block |
| `tests/e2e/test_backup.py` | 3 neue Tests |

Keine Änderung nötig an Aufrufstellen (`admin system backup`, `scripts/backup.py`),
da `restore_exports=False` der Default ist.

---

## Akzeptanzkriterium

- `restore_from(backup_path)` verhält sich identisch wie bisher (kein Bruch)
- `restore_from(backup_path, restore_exports=True)` kopiert `backup_dir/exports/`
  in `self._export_dir` zurück, sofern vorhanden
- `python -m pytest tests/e2e/test_backup.py` → alle Tests grün (inkl. 3 neue)
- `python -m pytest` → alle Tests grün (keine Regression)
