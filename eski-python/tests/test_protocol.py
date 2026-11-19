"""Cihaz gerektirmeyen testler: izin listesi ve olay çözümleme.

Çalıştır:  .venv\\Scripts\\python -m unittest discover tests
"""
import unittest

from quantum910p.protocol import (
    AncMode, MicState, SpatialMode, UnsafeWriteError, parse_event, validate_write,
)


class ValidateWriteTests(unittest.TestCase):
    def test_allowed_writes(self):
        validate_write("feature", [0x46, AncMode.TALKTHRU])
        validate_write("output", [0x72, SpatialMode.FIXED, SpatialMode.OFF])

    def test_forbidden_reports_rejected(self):
        for kind, data in [
            ("output", [0x06] + [0] * 61),   # RACE kanalı
            ("feature", [0xF0, 0x00]),       # firmware/bakım
            ("feature", [0xFB] + [0] * 63),
            ("feature", [0x5E, 0x00]),       # yeniden merkezle (kapsam dışı)
            ("feature", [0x72, 0x01, 0x00]), # 0x72 Feature olarak yazılmaz
            ("output", [0x46, 0x01]),        # 0x46 Output olarak yazılmaz
        ]:
            with self.subTest(kind=kind, rid=hex(data[0])):
                with self.assertRaises(UnsafeWriteError):
                    validate_write(kind, data)

    def test_bad_value_or_length_rejected(self):
        with self.assertRaises(UnsafeWriteError):
            validate_write("feature", [0x46, 0x03])
        with self.assertRaises(UnsafeWriteError):
            validate_write("feature", [0x46, 0x01, 0x00])
        with self.assertRaises(UnsafeWriteError):
            validate_write("output", [0x72, 0x01, 0xFF])
        with self.assertRaises(UnsafeWriteError):
            validate_write("feature", [])


class ParseEventTests(unittest.TestCase):
    def test_known_events(self):
        pad = [0xAA] * 62  # Windows'taki 64 bayt dolgusunu taklit et
        cases = [
            ([0x02, 0x01], "anc", AncMode.ANC),
            ([0x06, 0x00], "mic", MicState.MUTED),
            ([0x08, 0x32], "battery", 50),
            ([0x10, 0x08], "balance", 8),
            ([0x72, 0x02], "spatial", SpatialMode.HEAD_TRACKING),
        ]
        for data, name, value in cases:
            with self.subTest(name=name):
                ev = parse_event(data + pad)
                self.assertEqual(ev.name, name)
                self.assertEqual(ev.value, value)
                self.assertEqual(ev.raw[:2], bytes(data))

    def test_padding_trimmed(self):
        ev = parse_event([0x02, 0x00] + [0xAA] * 62)
        self.assertEqual(ev.raw, bytes([0x02, 0x00]))

    def test_unknown_value_kept_as_int(self):
        ev = parse_event([0x02, 0x07])
        self.assertEqual(ev.value, 7)
        self.assertNotIsInstance(ev.value, AncMode)

    def test_unknown_report(self):
        ev = parse_event([0x09, 0x01])
        self.assertEqual(ev.name, "unknown")

    def test_head_tracking(self):
        self.assertEqual(parse_event([0x05] + [0] * 20).name, "head_tracking")

    def test_empty(self):
        self.assertIsNone(parse_event([]))


if __name__ == "__main__":
    unittest.main()
