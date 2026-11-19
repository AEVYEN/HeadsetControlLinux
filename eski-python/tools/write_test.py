"""JBL Quantum 910P – yazma testi: ANC (Feature 0x46) ve mekânsal ses (Output 0x72).

Amaç: bu iki komut QuantumEngineService durdurulmuşken de çalışıyor mu?

Güvenlik:
- Sadece izin listesindeki iki rapora yazar, sadece doğrulanmış değerlerle.
- Okuma sadece resmi uygulamanın da okuduğu Feature'lardan yapılır (0x45, 0x72).
- Test bitince her iki ayar başlangıçtaki değerine geri döner.
"""
import time

import hid

VID, PID = 0x0ECB, 0x20A2
CONTROL_USAGE_PAGE = 0xFF13  # ana kontrol kanalı (COL01)

ANC_MODES = {0x00: "Kapalı", 0x01: "ANC", 0x02: "TalkThru"}
SPATIAL_MODES = {0x00: "Kapalı", 0x01: "Sabit", 0x02: "Kafa takibi"}

# İzin listesi: (tür, Report ID) -> (uzunluk ID dahil, veri baytlarında izinli değerler)
WRITABLE = {
    ("feature", 0x46): (2, {0x00, 0x01, 0x02}),  # ortam sesi: [46, mod]
    ("output", 0x72): (3, {0x00, 0x01, 0x02}),   # mekânsal ses: [72, yeni, önceki]
}

CONFIRM_TIMEOUT = 1.0  # sn; ANC onayı 70–500 ms içinde geliyordu
PAUSE = 1.5            # sn; adımlar arasında kulaklığa zaman tanı


def safe_write(dev, kind, data):
    """Sadece izin listesindeki rapora, izinli değerlerle yazar."""
    data = list(data)
    key = (kind, data[0])
    if key not in WRITABLE:
        raise ValueError(f"İzin listesinde değil: {kind} 0x{data[0]:02X}")
    length, allowed = WRITABLE[key]
    if len(data) != length:
        raise ValueError(f"Yanlış uzunluk: {len(data)} (beklenen {length})")
    if any(b not in allowed for b in data[1:]):
        raise ValueError(f"İzinsiz değer: {data}")

    if kind == "feature":
        written = dev.send_feature_report(data)
    else:
        written = dev.write(data)
    if written < 0:
        raise OSError(f"Yazma başarısız: {dev.error()}")


def read_feature(dev, rid, length):
    """Resmi uygulamanın da okuduğu bir Feature'ı okur, [ID, veri...] döndürür."""
    data = dev.get_feature_report(rid, 64)[:length]
    if len(data) < length or data[0] != rid:
        raise OSError(f"Feature 0x{rid:02X} için beklenmeyen cevap: {data}")
    return data


def drain(dev):
    """Bekleyen olayları boşaltır ki eski bir olay onay sanılmasın."""
    while dev.read(64, 50):
        pass


def wait_for_event(dev, rid, timeout):
    """rid olayını bekler; (değer, gecikme ms) ya da (None, None) döndürür."""
    start = time.monotonic()
    while (elapsed := time.monotonic() - start) < timeout:
        data = dev.read(64, 50)
        if data and data[0] == rid and len(data) >= 2:
            return data[1], int(elapsed * 1000)
    return None, None


def test_sequence(original):
    """Başlangıçtan farklı iki modu dener, sonra başlangıca döner."""
    others = [m for m in (0x01, 0x02, 0x00) if m != original]
    return others + [original]


def test_anc(dev):
    print("=== ANC testi (Feature 0x46) ===")
    original = read_feature(dev, 0x45, 2)[1]
    print(f"Başlangıç: {ANC_MODES[original]}")
    results = []
    for target in test_sequence(original):
        drain(dev)
        safe_write(dev, "feature", [0x46, target])
        event, delay = wait_for_event(dev, 0x02, CONFIRM_TIMEOUT)
        state = read_feature(dev, 0x45, 2)[1]

        event_text = f"{ANC_MODES.get(event, event)} ({delay} ms)" if event is not None else "gelmedi"
        ok = state == target
        results.append(ok)
        print(f"  -> {ANC_MODES[target]:<9} olay 0x02: {event_text:<16} "
              f"Feature 0x45: {ANC_MODES.get(state, state):<9} {'✓' if ok else '✗'}")
        time.sleep(PAUSE)
    return results


def test_spatial(dev):
    print("=== Mekânsal ses testi (Output 0x72) ===")
    original = read_feature(dev, 0x72, 3)[1]
    print(f"Başlangıç: {SPATIAL_MODES[original]}")
    results = []
    for target in test_sequence(original):
        current = read_feature(dev, 0x72, 3)[1]
        safe_write(dev, "output", [0x72, target, current])

        # Onay olayı yok; Feature 0x72'yi hedefe ulaşana kadar yokla.
        start = time.monotonic()
        state = current
        while time.monotonic() - start < CONFIRM_TIMEOUT:
            state = read_feature(dev, 0x72, 3)[1]
            if state == target:
                break
            time.sleep(0.05)
        delay = int((time.monotonic() - start) * 1000)

        ok = state == target
        results.append(ok)
        print(f"  -> {SPATIAL_MODES[target]:<12} Feature 0x72: "
              f"{SPATIAL_MODES.get(state, state):<12} ({delay} ms) {'✓' if ok else '✗'}")
        time.sleep(PAUSE)
    return results


def find_control_path():
    for d in hid.enumerate(VID, PID):
        if d["usage_page"] == CONTROL_USAGE_PAGE:
            return d["path"]
    return None


def main():
    path = find_control_path()
    if path is None:
        print("Dongle bulunamadı. Takılı mı?")
        return

    print("Bu betik ANC ve mekânsal ses ayarını birkaç kez değiştirip")
    print("sonunda başlangıç değerlerine geri döndürecek.")
    print("QuantumEngineService durdurulmuş ve QuantumENGINE kapalı olmalı.")
    if input("Devam etmek için e yaz: ").strip().lower() != "e":
        print("İptal edildi.")
        return

    dev = hid.device()
    dev.open_path(path)
    try:
        anc = test_anc(dev)
        print()
        spatial = test_spatial(dev)
    finally:
        dev.close()

    print()
    print(f"ANC:          {sum(anc)}/{len(anc)} başarılı")
    print(f"Mekânsal ses: {sum(spatial)}/{len(spatial)} başarılı")


if __name__ == "__main__":
    main()