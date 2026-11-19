"""JBL Quantum 910P – kulaklığın durumunu okur ve olayları dinler.

Açılışta mevcut durumu Feature raporlarından okur (resmi uygulamanın da okuduğu
raporlar), sonra kulaklıktan gelen olayları dinler.
Bu betik cihaza HİÇBİR ŞEY YAZMAZ, sadece okur.
"""
import time

import hid

VID, PID = 0x0ECB, 0x20A2
CONTROL_USAGE_PAGE = 0xFF13  # ana kontrol kanalı (COL01)

# 0x05 kafa takibi akışı saniyede ~100 paket gelir; True yaparsan ekrana basar.
SHOW_HEAD_TRACKING = False

# Input rapor uzunlukları (Report ID dahil), descriptor'dan.
# Windows'ta hidapi her paketi 64 bayta tamamlıyor; fazlası eski veri.
INPUT_LENGTHS = {
    0x02: 2, 0x03: 2, 0x04: 2, 0x05: 21, 0x06: 2, 0x07: 2, 0x08: 2,
    0x09: 2, 0x10: 2, 0x29: 64, 0x4C: 4, 0x4D: 8, 0x5C: 2, 0x72: 3,
    0x75: 2,
}

ANC_MODES = {0x00: "Kapalı", 0x01: "ANC", 0x02: "TalkThru"}
MIC_STATES = {0x00: "Sessiz", 0x01: "Açık"}
SPATIAL_MODES = {0x00: "Kapalı", 0x01: "Sabit", 0x02: "Kafa takibi"}


def unknown(value):
    return f"Bilinmiyor (0x{value:02X})"


def anc(value):
    return ANC_MODES.get(value, unknown(value))


def mic(value):
    return MIC_STATES.get(value, unknown(value))


def spatial(value):
    return SPATIAL_MODES.get(value, unknown(value))


def balance(value):
    """0x00 = tam Chat, 0x08 = orta, 0x10 = tam Game."""
    labels = {0x00: "tam Chat", 0x08: "orta", 0x10: "tam Game"}
    label = labels.get(value, "Chat tarafı" if value < 0x08 else "Game tarafı")
    return f"{value}/16 ({label})"


def battery(value):
    return f"%{value}"


# Olaylar: Report ID -> (ad, çözümleyici). Değer her zaman 2. bayt.
EVENTS = {
    0x02: ("Ortam sesi", anc),
    0x06: ("Mikrofon", mic),
    0x08: ("Pil", battery),
    0x10: ("Game/Chat", balance),
    0x72: ("Mekânsal ses", spatial),
}

# Açılışta okunan Feature'lar: (Report ID, uzunluk ID dahil, ad, çözümleyici).
# Hepsi resmi uygulamanın da okuduğu raporlar.
STARTUP_FEATURES = [
    (0x45, 2, "Ortam sesi", anc),
    (0x62, 2, "Game/Chat", balance),
    (0x67, 2, "Mikrofon", mic),
    (0x72, 3, "Mekânsal ses", spatial),
    (0x49, 2, "Pil", battery),
]


def hexstr(data):
    return " ".join(f"{b:02X}" for b in data)


def find_control_path():
    """Dongle'ın 0xFF13 kanalının yolunu bulur."""
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == CONTROL_USAGE_PAGE:
            return d["path"]
    return None


def read_initial_state(dev):
    print("Mevcut durum:")
    for rid, length, name, decode in STARTUP_FEATURES:
        try:
            data = dev.get_feature_report(rid, 64)[:length]
        except OSError as e:
            print(f"  {name:<13} okunamadı ({e})")
            continue
        if len(data) < length or data[0] != rid:
            print(f"  {name:<13} beklenmeyen cevap: {hexstr(data)}")
            continue
        print(f"  {name:<13} {decode(data[1])}")
    print()


def main():
    path = find_control_path()
    if path is None:
        print("Dongle bulunamadı. Takılı mı?")
        return

    dev = hid.device()
    dev.open_path(path)
    try:
        read_initial_state(dev)
        print("Olaylar dinleniyor... Çıkmak için Ctrl+C")
        last_head_tracking = 0.0
        while True:
            data = dev.read(64, 500)  # en fazla 64 bayt, 500 ms bekle
            if not data:
                continue  # bu 500 ms içinde olay yok, tekrar dene

            rid = data[0]
            data = data[:INPUT_LENGTHS.get(rid, len(data))]
            now = time.strftime("%H:%M:%S")

            if rid == 0x05 and not SHOW_HEAD_TRACKING:
                # Akış başladığında bir kez haber ver, sonra sessiz kal.
                if time.monotonic() - last_head_tracking > 1.0:
                    print(f"{now}  05 ...  -> Kafa takibi akışı (gizleniyor)")
                last_head_tracking = time.monotonic()
                continue

            if rid in EVENTS and len(data) >= 2:
                name, decode = EVENTS[rid]
                print(f"{now}  {hexstr(data)}  -> {name}: {decode(data[1])}")
            else:
                print(f"{now}  {hexstr(data)}  -> (henüz bilinmeyen rapor)")
    except KeyboardInterrupt:
        print("\nÇıkılıyor.")
    finally:
        dev.close()


if __name__ == "__main__":
    main()