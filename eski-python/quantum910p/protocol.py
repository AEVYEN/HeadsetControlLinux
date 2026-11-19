"""JBL Quantum 910P – protokol tanımları.

Bu modül cihaza HİÇ dokunmaz: sadece bayt <-> anlam çevirisi ve güvenlik
izin listeleri. Böylece kulaklık takılı olmadan test edilebilir.
Kaynak ve ayrıntılar: protocol.md
"""
from dataclasses import dataclass
from enum import IntEnum

VID, PID = 0x0ECB, 0x20A2
CONTROL_USAGE_PAGE = 0xFF13  # ana kontrol kanalı (COL01)
READ_SIZE = 64               # hidapi Windows'ta her paketi 64 bayta tamamlıyor


class AncMode(IntEnum):
    OFF = 0x00
    ANC = 0x01
    TALKTHRU = 0x02


class SpatialMode(IntEnum):
    OFF = 0x00
    FIXED = 0x01          # açık, kafa takipsiz
    HEAD_TRACKING = 0x02


class MicState(IntEnum):
    MUTED = 0x00
    ON = 0x01


BALANCE_MAX = 0x10  # 0x00 tam Chat, 0x08 orta, 0x10 tam Game (17 kademe)

# --- Report ID'ler -----------------------------------------------------------

FEATURE_ANC_STATE = 0x45   # okuma: ANC durumu
FEATURE_ANC_SET = 0x46     # yazma: ANC ayarla (okuması hep 00, kullanılmaz)
FEATURE_BATTERY = 0x49
FEATURE_BALANCE = 0x62
FEATURE_MIC = 0x67
REPORT_SPATIAL = 0x72      # Feature okuma, Output yazma, Input olay

INPUT_ANC = 0x02
INPUT_HEAD_TRACKING = 0x05
INPUT_MIC = 0x06
INPUT_BATTERY = 0x08
INPUT_BALANCE = 0x10
INPUT_SPATIAL = 0x72

# Input rapor uzunlukları (Report ID dahil), descriptor'dan.
INPUT_LENGTHS = {
    0x02: 2, 0x03: 2, 0x04: 2, 0x05: 21, 0x06: 2, 0x07: 2, 0x08: 2,
    0x09: 2, 0x10: 2, 0x29: 64, 0x4C: 4, 0x4D: 8, 0x5C: 2, 0x72: 3,
    0x75: 2,
}

# --- ⚠️ Güvenlik izin listeleri ---------------------------------------------
# Okuma: sadece resmi uygulamanın da okuduğu Feature'lar. Değer: uzunluk (ID dahil).
READABLE_FEATURES = {
    FEATURE_ANC_STATE: 2,
    FEATURE_BATTERY: 2,
    FEATURE_BALANCE: 2,
    FEATURE_MIC: 2,
    REPORT_SPATIAL: 3,
}

# Yazma: (tür, Report ID) -> (uzunluk ID dahil, izinli veri baytları)
WRITABLE = {
    ("feature", FEATURE_ANC_SET): (2, frozenset(AncMode)),
    ("output", REPORT_SPATIAL): (3, frozenset(SpatialMode)),
}


# ASLA dokunulmayacaklar (protocol.md "Güvenlik kuralları"). İzin listesi zaten
# bunları dışarıda bırakıyor; bu liste ikinci kilit: biri yanlışlıkla izin
# listesine eklerse modül hiç yüklenmez.
FORBIDDEN = frozenset({
    ("output", 0x06),  # Airoha RACE komut kanalı (Input 0x06 = mikrofon olayı, o zararsız)
    *(("feature", rid) for rid in (0xF0, 0xF1, 0xF4, 0xF5, 0xF6, 0xFA, 0xFB)),  # firmware/bakım
    ("feature", 0x9A),  # COL02, anlamı bilinmiyor
})

_clash = FORBIDDEN & (set(WRITABLE) | {("feature", rid) for rid in READABLE_FEATURES})
if _clash:
    raise RuntimeError(f"Yasaklı rapor izin listesinde: {sorted(_clash)}")


class UnsafeWriteError(ValueError):
    """İzin listesi dışında bir yazma denemesi. Asla cihaza gitmez."""


def validate_write(kind: str, data: list[int]) -> None:
    """Yazılacak raporu izin listesine göre denetler; uygun değilse hata fırlatır."""
    if not data:
        raise UnsafeWriteError("Boş rapor")
    key = (kind, data[0])
    if key not in WRITABLE:
        raise UnsafeWriteError(f"İzin listesinde değil: {kind} 0x{data[0]:02X}")
    length, allowed = WRITABLE[key]
    if len(data) != length:
        raise UnsafeWriteError(f"Yanlış uzunluk: {len(data)} (beklenen {length})")
    if any(b not in allowed for b in data[1:]):
        raise UnsafeWriteError(f"İzinsiz değer: {hexstr(data)}")


# --- Durum ve olaylar ----------------------------------------------------------

@dataclass(frozen=True)
class State:
    anc: AncMode | int
    balance: int            # 0..16
    mic: MicState | int
    spatial: SpatialMode | int
    battery: int            # yüzde


@dataclass(frozen=True)
class Event:
    report_id: int
    name: str               # "anc", "mic", "battery", "balance", "spatial", "head_tracking", "unknown"
    value: object           # çözülmüş değer; bilinmeyen raporlarda None
    raw: bytes


def to_enum(cls, value: int):
    """Bilinen değeri enum'a çevirir; bilinmeyen değeri ham int olarak bırakır.

    Firmware güncellemesi yeni bir mod eklerse kütüphane çökmesin diye.
    """
    try:
        return cls(value)
    except ValueError:
        return value


# Report ID -> (olay adı, değer çözümleyici). Değer her zaman 2. bayt.
_EVENT_DECODERS = {
    INPUT_ANC: ("anc", lambda v: to_enum(AncMode, v)),
    INPUT_MIC: ("mic", lambda v: to_enum(MicState, v)),
    INPUT_BATTERY: ("battery", int),
    INPUT_BALANCE: ("balance", int),
    INPUT_SPATIAL: ("spatial", lambda v: to_enum(SpatialMode, v)),
}


def parse_event(data) -> Event | None:
    """Ham interrupt paketini Event'e çevirir. Boş paket için None."""
    if not data:
        return None
    rid = data[0]
    raw = bytes(data[:INPUT_LENGTHS.get(rid, len(data))])

    if rid == INPUT_HEAD_TRACKING:
        return Event(rid, "head_tracking", None, raw)
    if rid in _EVENT_DECODERS and len(raw) >= 2:
        name, decode = _EVENT_DECODERS[rid]
        return Event(rid, name, decode(raw[1]), raw)
    return Event(rid, "unknown", None, raw)


def hexstr(data) -> str:
    return " ".join(f"{b:02X}" for b in data)
