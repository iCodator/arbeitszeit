import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from arbeitszeit.infrastructure.config_file import (
    AdminConfig,
    AppConfig,
    BackupConfig,
    DatabaseConfig,
    TerminalConfig,
    find_config,
    load_config,
    write_config,
)

_MINIMAL_TOML = b"""
[database]
path = "/tmp/arbeitszeit.db"
"""

_FULL_TOML = b"""
[database]
path = "/home/user/data/arbeitszeit.db"

[terminal]
id = 1
numpad = "Test Numpad"
rfid = "Test RFID Reader"

[backup]
backup_dir = "/var/backups/arbeitszeit"
export_dir = "/var/exports/arbeitszeit"
log_dir = "/var/log/arbeitszeit"

[admin]
user_id = 42
"""


# ---------------------------------------------------------------------------
# find_config
# ---------------------------------------------------------------------------


def test_find_config_gibt_none_wenn_kein_file(tmp_path, monkeypatch):
    monkeypatch.delenv("ARBEITSZEIT_CONFIG", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(tmp_path)
    assert find_config() is None


def test_find_config_env_wird_zurueckgegeben(tmp_path, monkeypatch):
    env_path = tmp_path / "my_config.toml"
    monkeypatch.setenv("ARBEITSZEIT_CONFIG", str(env_path))
    assert find_config() == env_path


def test_find_config_env_hat_vorrang_vor_xdg(tmp_path, monkeypatch):
    env_path = tmp_path / "env_config.toml"
    monkeypatch.setenv("ARBEITSZEIT_CONFIG", str(env_path))
    fake_home = tmp_path / "home"
    xdg_dir = fake_home / ".config" / "arbeitszeit"
    xdg_dir.mkdir(parents=True)
    (xdg_dir / "config.toml").write_bytes(b"")
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    assert find_config() == env_path


def test_find_config_xdg(tmp_path, monkeypatch):
    monkeypatch.delenv("ARBEITSZEIT_CONFIG", raising=False)
    fake_home = tmp_path / "home"
    xdg_dir = fake_home / ".config" / "arbeitszeit"
    xdg_dir.mkdir(parents=True)
    xdg_config = xdg_dir / "config.toml"
    xdg_config.write_bytes(b"")
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.chdir(tmp_path)
    assert find_config() == xdg_config


def test_find_config_lokal(tmp_path, monkeypatch):
    monkeypatch.delenv("ARBEITSZEIT_CONFIG", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "empty_home")
    local_config = tmp_path / "config.toml"
    local_config.write_bytes(b"")
    monkeypatch.chdir(tmp_path)
    assert find_config() == local_config


def test_find_config_xdg_hat_vorrang_vor_lokal(tmp_path, monkeypatch):
    monkeypatch.delenv("ARBEITSZEIT_CONFIG", raising=False)
    fake_home = tmp_path / "home"
    xdg_dir = fake_home / ".config" / "arbeitszeit"
    xdg_dir.mkdir(parents=True)
    xdg_config = xdg_dir / "config.toml"
    xdg_config.write_bytes(b"")
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    (tmp_path / "config.toml").write_bytes(b"")
    monkeypatch.chdir(tmp_path)
    assert find_config() == xdg_config


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


def test_load_config_minimal(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(_MINIMAL_TOML)
    config = load_config(config_file)
    assert config.database.path == Path("/tmp/arbeitszeit.db")
    assert config.terminal.id is None
    assert config.terminal.numpad is None
    assert config.terminal.rfid is None
    assert config.backup.backup_dir is None
    assert config.admin.user_id is None


def test_load_config_alle_felder(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(_FULL_TOML)
    config = load_config(config_file)
    assert config.database.path == Path("/home/user/data/arbeitszeit.db")
    assert config.terminal.id == 1
    assert config.terminal.numpad == "Test Numpad"
    assert config.terminal.rfid == "Test RFID Reader"
    assert config.backup.backup_dir == Path("/var/backups/arbeitszeit")
    assert config.backup.export_dir == Path("/var/exports/arbeitszeit")
    assert config.backup.log_dir == Path("/var/log/arbeitszeit")
    assert config.admin.user_id == 42


def test_load_config_leere_datei_gibt_defaults(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(b"")
    assert load_config(config_file) == AppConfig()


def test_load_config_unbekannte_schluessel_werden_ignoriert(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(b"[unbekannt]\nfoo = 42\n")
    assert load_config(config_file) == AppConfig()


# ---------------------------------------------------------------------------
# write_config
# ---------------------------------------------------------------------------


def test_write_config_roundtrip(tmp_path):
    original = AppConfig(
        database=DatabaseConfig(path=Path("/home/user/arbeitszeit.db")),
        terminal=TerminalConfig(id=2, numpad="USB Numpad", rfid="RFID Reader"),
        backup=BackupConfig(
            backup_dir=Path("/var/backups"),
            export_dir=Path("/var/exports"),
            log_dir=Path("/var/log/arbeitszeit"),
        ),
        admin=AdminConfig(user_id=7),
    )
    config_file = tmp_path / "config.toml"
    write_config(original, config_file)
    assert load_config(config_file) == original


def test_write_config_nur_gesetzte_sektionen(tmp_path):
    config = AppConfig(database=DatabaseConfig(path=Path("/tmp/test.db")))
    config_file = tmp_path / "config.toml"
    write_config(config, config_file)
    content = config_file.read_text(encoding="utf-8")
    assert "[database]" in content
    assert "[terminal]" not in content
    assert "[backup]" not in content
    assert "[admin]" not in content


def test_write_config_erstellt_verzeichnis(tmp_path):
    config = AppConfig(database=DatabaseConfig(path=Path("/tmp/test.db")))
    nested = tmp_path / "sub" / "dir" / "config.toml"
    write_config(config, nested)
    assert nested.is_file()


def test_write_config_leer_wenn_alles_none(tmp_path):
    config_file = tmp_path / "config.toml"
    write_config(AppConfig(), config_file)
    assert config_file.read_text(encoding="utf-8").strip() == ""


def test_write_config_sonderzeichen_in_geraetename(tmp_path):
    config = AppConfig(
        terminal=TerminalConfig(rfid='Device "with" quotes'),
    )
    config_file = tmp_path / "config.toml"
    write_config(config, config_file)
    loaded = load_config(config_file)
    assert loaded.terminal.rfid == 'Device "with" quotes'
