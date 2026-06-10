# Programmieraufgabe: `FakeUnitOfWork.__exit__` an reale commit-or-rollback-Semantik angleichen

## Herleitung aus `phase3_planung.md`

Das Dokument beschreibt `FakeUnitOfWork.__exit__` mit:

> „Ruft `rollback()` bei Exception, damit Tests das reale Transaktionsverhalten
> widerspiegeln."

Die **reale** Semantik von `SQLiteUnitOfWork` ist jedoch strenger und weicht davon ab:

> „Jede Transaktion, die nicht explizit per `commit()` bestätigt wurde, wird beim
> Verlassen des `with`-Blocks automatisch zurückgerollt — auch bei fehlerfreiem
> Ablauf." (`planung_gesamt.md`, Abschnitt `SQLiteUnitOfWork`)

Das Planungsdokument hält fest, dass der Integrationstest
`test_vergessenes_commit_rollt_automatisch_zurueck` diese Semantik für die echte UoW
explizit absichert. Die `FakeUnitOfWork` widerspiegelt diese Semantik jedoch **nicht**.

---

## Befund

**`FakeUnitOfWork.__exit__`** (`tests/application/fakes.py`):

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is not None:          # ← nur bei Exception
        self.rollback()
```

**`SQLiteUnitOfWork.__exit__`** (`src/arbeitszeit/infrastructure/db/unit_of_work.py`):

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if self._transaction_open:        # ← bei JEDER unkonfirmierten Transaktion
        self.rollback()
```

Konsequenz: Verlässt ein Use Case den `with`-Block sauber **ohne `commit()`** (z. B.
durch eine stille Rückgabe vor dem Commit-Aufruf), rollt die echte UoW automatisch
zurück — die Fake tut **nichts**. Die Fake-Tests können diesen Fall nicht auffangen.

Außerdem: Das Integrationstest-Gegenstück für die Fake fehlt vollständig. Für die
echte UoW existiert `test_vergessenes_commit_rollt_automatisch_zurueck`; für
`FakeUnitOfWork` gibt es keinen analogen Test.

---

## Aufgabe

**`FakeUnitOfWork.__exit__` korrigieren und mit einem Test absichern.**

### 1. `fakes.py`: `__exit__` auf commit-or-rollback umstellen

Vorher:
```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is not None:
        self.rollback()
```

Nachher:
```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if not self.committed:
        self.rollback()
```

Semantik nach der Änderung:

| Situation | `committed` | Aktion in `__exit__` |
|---|---|---|
| `commit()` wurde gerufen, kein Fehler | `True` | kein rollback ✓ |
| `commit()` wurde gerufen, danach Exception | `True` | kein rollback ✓ |
| `commit()` vergessen, sauberer Exit | `False` | `rollback()` ✓ |
| `commit()` vergessen, Exception | `False` | `rollback()` ✓ |

Dies entspricht exakt dem Verhalten von `SQLiteUnitOfWork` (dort via
`_transaction_open`-Flag).

### 2. `tests/application/fakes.py` oder neues Testmodul: Gegentest ergänzen

Analog zu `test_vergessenes_commit_rollt_automatisch_zurueck` in
`tests/integration/test_unit_of_work.py` einen Test für die Fake hinzufügen:

```python
def test_fake_uow_vergessenes_commit_setzt_rolled_back():
    uow = FakeUnitOfWork()
    with uow:
        uow.time_booking_repo.add(...)
        # commit() absichtlich weggelassen
    assert uow.rolled_back is True
    assert uow.committed is False


def test_fake_uow_korrekter_commit_kein_rollback():
    uow = FakeUnitOfWork()
    with uow:
        uow.commit()
    assert uow.committed is True
    assert uow.rolled_back is False
```

---

## Betroffene Dateien

| Datei | Änderung |
|---|---|
| `tests/application/fakes.py` | `FakeUnitOfWork.__exit__`: `exc_type is not None` → `not self.committed` |
| `tests/application/fakes.py` | 2 Tests ergänzen (vergessenes Commit + korrekter Commit) |

Keine Änderung nötig an Use-Case-Code oder Produktionscode — alle Use Cases rufen
`commit()` korrekt auf; die Tests für Erfolgspfade prüfen bereits `uow.committed`.

---

## Akzeptanzkriterium

- `FakeUnitOfWork` ohne `commit()` verlassen → `uow.rolled_back is True`
- `FakeUnitOfWork` mit `commit()` verlassen → `uow.rolled_back is False`
- `python -m pytest tests/application/` → alle Tests weiterhin grün
  (Use Cases rufen `commit()` korrekt auf — Verhalten bleibt identisch)
- `python -m pytest` → alle Tests grün (keine Regression)
