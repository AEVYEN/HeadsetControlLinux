"""Pil izleme – uzun süre açık bırakılır (oyun, film boyunca).

Cevaplanacak sorular (protocol.md, Açık sorular):
  1. Pil değişince Input 0x08 olayı kendiliğinden geliyor mu?
  2. Pil 5'er mi bildiriliyor?

Feature 0x49 okuması 0x08 olayını tetikliyor olabilir (hipotez). Bu yüzden
seyrek okunur ve okumadan hemen sonra gelen 0x08 "tetiklenmiş" diye ayrılır.
Bilinmeyen olaylar (ör. 0x03 / 0x09) de kaydedilir.

Sadece OKUR. Kayıt: battery_log.csv (proje kökü). Çıkmak için Ctrl+C.
"""
import csv
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quantum910p import Headset, HeadsetError  # noqa: E402
from quantum910p.protocol import hexstr  # noqa: E402

POLL_EVERY = 120.0     # sn; Feature 0x49 okuma aralığı (seyrek tut)
TRIGGER_WINDOW = 1.0   # sn; okumadan bu kadar sonra gelen 0x08 "tetiklenmiş" sayılır
LOG = ROOT / "battery_log.csv"


def main():
    new_file = not LOG.exists()
    with Headset() as hs, LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["zaman", "kaynak", "pil", "ham"])

        last_value = None

        def log(source, value, raw=b""):
            nonlocal last_value
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            note = ""
            if isinstance(value, int) and last_value is not None and value != last_value:
                note = f"   <-- değişti: %{last_value} -> %{value}"
            if isinstance(value, int):
                last_value = value
            shown = f"%{value}" if isinstance(value, int) else value
            print(f"{now}  {source:<28} {shown}{note}")
            writer.writerow([now, source, value, hexstr(raw)])
            f.flush()  # Ctrl+C'de kayıt kaybolmasın

        print(f"Kayıt: {LOG}")
        print(f"Feature 0x49 her {POLL_EVERY:.0f} sn'de bir okunuyor. Çıkmak için Ctrl+C\n")

        last_read = -math.inf
        while True:
            if time.monotonic() - last_read >= POLL_EVERY:
                last_read = time.monotonic()
                try:
                    log("okuma 0x49", hs.battery())
                except HeadsetError as e:  # kulaklık kapalıyken ne olduğu da bilgi
                    log("okuma 0x49", f"okunamadı ({e})")

            ev = hs.read_event(500)
            if ev is None or ev.name == "head_tracking":
                continue
            if ev.name == "battery":
                triggered = time.monotonic() - last_read < TRIGGER_WINDOW
                source = "olay 0x08 (okuma sonrası)" if triggered else "olay 0x08 KENDİLİĞİNDEN"
                log(source, ev.value, ev.raw)
            elif ev.name == "unknown":
                log(f"bilinmeyen 0x{ev.report_id:02X}", "-", ev.raw)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nÇıkılıyor.")
