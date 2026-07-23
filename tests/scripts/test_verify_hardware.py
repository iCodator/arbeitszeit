"""Tests für scripts/verify_hardware.py."""

__version__ = "1.0"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from verify_hardware import _mask_uid  # noqa: E402


class TestMaskUid:
    def test_volle_uid_zeigt_nur_erste_vier_zeichen(self) -> None:
        assert _mask_uid("aabbccdd") == "AABB****"

    def test_gross_und_kleinschreibung_normalisiert(self) -> None:
        assert _mask_uid("AABBCCDD") == "AABB****"

    def test_kurze_uid_kein_absturz(self) -> None:
        assert _mask_uid("ab") == "AB****"

    def test_leere_uid_liefert_nur_sternchen(self) -> None:
        assert _mask_uid("") == "****"

    def test_suffix_immer_vier_sternchen(self) -> None:
        result = _mask_uid("0011223344556677")
        assert result.endswith("****")
        assert result == "0011****"
