"""JBL Quantum 910P – cihaz erişimi (hidapi).

Cihaza konuşan TEK katman. Tüm okuma/yazmalar protocol.py'deki izin
listelerinden geçer. Linux'a geçerken değişecek yer burası.
"""
import time
from collections import deque

import hid

from .protocol import (
    CONTROL_USAGE_PAGE, FEATURE_ANC_SET, FEATURE_ANC_STATE, FEATURE_BALANCE,
    FEATURE_BATTERY, FEATURE_MIC, INPUT_ANC, PID, READ_SIZE, READABLE_FEATURES,
    REPORT_SPATIAL, VID, AncMode, Event, MicState, SpatialMode, State,
    hexstr, parse_event, to_enum, validate_write,
)

CONFIRM_TIMEOUT = 1.0  # sn; ANC onayı 70–500 ms içinde geliyordu
POLL_INTERVAL = 0.05   # sn; mekânsal ses onayını yoklama aralığı


class HeadsetError(Exception):
    pass


class DeviceNotFound(HeadsetError):
    pass


class ConfirmationError(HeadsetError):
    """Komut gönderildi ama cihaz istenen duruma geçmedi."""


class Headset:
    """Dongle'ın 0xFF13 kontrol kanalı.

    Kullanım:
        with Headset() as hs:
            print(hs.read_state())
            hs.set_anc(AncMode.ANC)
            for ev in hs.events():
                ...
    """

    def __init__(self, path: bytes | None = None):
        self._path = path
        self._dev = None
        # Onay beklerken gelen başka olaylar burada bekler; events() önce bunları verir.
        self._pending: deque[Event] = deque()

    # --- bağlantı ---------------------------------------------------------------

    @staticmethod
    def find_path() -> bytes | None:
        for d in hid.enumerate(VID, PID):
            if d["usage_page"] == CONTROL_USAGE_PAGE:
                return d["path"]
        return None

    def open(self) -> "Headset":
        path = self._path or self.find_path()
        if path is None:
            raise DeviceNotFound("Dongle bulunamadı. Takılı mı?")
        self._dev = hid.device()
        self._dev.open_path(path)
        return self

    def close(self) -> None:
        if self._dev is not None:
            self._dev.close()
            self._dev = None

    def __enter__(self) -> "Headset":
        return self.open()

    def __exit__(self, *exc) -> None:
        self.close()

    # --- düşük seviye (izin listeli) -----------------------------------------------

    def _read_feature(self, rid: int) -> bytes:
        if rid not in READABLE_FEATURES:
            raise HeadsetError(f"Okuma izin listesinde değil: Feature 0x{rid:02X}")
        length = READABLE_FEATURES[rid]
        data = bytes(self._dev.get_feature_report(rid, READ_SIZE)[:length])
        if len(data) < length or data[0] != rid:
            raise HeadsetError(f"Feature 0x{rid:02X} için beklenmeyen cevap: {hexstr(data)}")
        return data

    def _write(self, kind: str, data: list[int]) -> None:
        data = [int(b) for b in data]
        validate_write(kind, data)  # izinsizse burada durur, cihaza gitmez
        if kind == "feature":
            written = self._dev.send_feature_report(data)
        else:
            written = self._dev.write(data)
        if written < 0:
            raise HeadsetError(f"Yazma başarısız: {self._dev.error()}")

    def _read_event(self, timeout_ms: int) -> Event | None:
        return parse_event(self._dev.read(READ_SIZE, timeout_ms))

    def _wait_for(self, report_id: int, timeout: float) -> Event | None:
        """report_id olayını bekler. Araya giren diğer olaylar kaybolmaz, kuyruğa girer."""
        deadline = time.monotonic() + timeout
        while (left := deadline - time.monotonic()) > 0:
            ev = self._read_event(max(1, int(left * 1000)))
            if ev is None:
                continue
            if ev.report_id == report_id:
                return ev
            self._pending.append(ev)
        return None

    # --- durum okuma ----------------------------------------------------------

    def anc(self) -> AncMode | int:
        return to_enum(AncMode, self._read_feature(FEATURE_ANC_STATE)[1])

    def balance(self) -> int:
        return self._read_feature(FEATURE_BALANCE)[1]

    def mic(self) -> MicState | int:
        return to_enum(MicState, self._read_feature(FEATURE_MIC)[1])

    def spatial(self) -> SpatialMode | int:
        return to_enum(SpatialMode, self._read_feature(REPORT_SPATIAL)[1])

    def battery(self) -> int:
        return self._read_feature(FEATURE_BATTERY)[1]

    def read_state(self) -> State:
        return State(
            anc=self.anc(),
            balance=self.balance(),
            mic=self.mic(),
            spatial=self.spatial(),
            battery=self.battery(),
        )

    # --- ayarlama ----------------------------------------------------------------

    def set_anc(self, mode: AncMode, timeout: float = CONFIRM_TIMEOUT) -> AncMode:
        """Ortam sesi modunu ayarlar (Feature 0x46) ve cihazın onayını bekler.

        Bilinen: kulaklık 70–500 ms içinde Input 0x02 olayıyla onaylıyor,
        Feature 0x45 de gerçek durumu gösteriyor.
        """
        mode = AncMode(mode)
        # Komut başka bir olay beklerken kaybolmasın diye eski 0x02'ler onay sanılmamalı:
        self._pending = deque(e for e in self._pending if e.report_id != INPUT_ANC)
        self._write("feature", [FEATURE_ANC_SET, mode])

        # TODO(sen): onay stratejisi. Elindeki araçlar:
        #   ev = self._wait_for(INPUT_ANC, timeout)   -> Event ya da None (zaman aşımı)
        #   ev.value                                  -> AncMode (ya da bilinmeyen int)
        #   self.anc()                                -> Feature 0x45'ten gerçek durum
        #   raise ConfirmationError("...")            -> başarısızlık
        # Dönüş: cihazın onayladığı mod.
        raise NotImplementedError

    def set_spatial(self, mode: SpatialMode, timeout: float = CONFIRM_TIMEOUT) -> SpatialMode:
        """Mekânsal ses modunu ayarlar (Output 0x72).

        Uygulamayı birebir taklit eder: [72, yeni, mevcut]. Onay olayı gelmediği
        için Feature 0x72 hedefe ulaşana kadar yoklanır.
        """
        mode = SpatialMode(mode)
        current = self.spatial()
        if current == mode:
            return mode
        if not isinstance(current, SpatialMode):
            # Bilinmeyen mevcut modu 3. bayta koymak izin listesini çiğner; dokunma.
            raise HeadsetError(f"Mevcut mekânsal ses modu bilinmiyor: 0x{current:02X}")
        self._write("output", [REPORT_SPATIAL, mode, current])

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.spatial() == mode:
                return mode
            time.sleep(POLL_INTERVAL)
        raise ConfirmationError(f"Mekânsal ses {mode.name} moduna geçmedi")

    # --- olaylar ------------------------------------------------------------------

    def read_event(self, timeout_ms: int = 500) -> Event | None:
        """Sıradaki olayı döndürür; timeout_ms içinde olay yoksa None."""
        if self._pending:
            return self._pending.popleft()
        return self._read_event(timeout_ms)

    def events(self, include_head_tracking: bool = False):
        """Olayları sonsuza kadar üretir (Ctrl+C ya da break ile çıkılır)."""
        while True:
            ev = self.read_event()
            if ev is None:
                continue
            if ev.name == "head_tracking" and not include_head_tracking:
                continue
            yield ev
