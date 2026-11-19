# JBL Quantum 910P – Cihaz Bilgisi

## Bağlantı
- Desteklenen: 2.4 GHz dongle
- Kapsam dışı: USB-C kablo, Bluetooth

## Dongle
- VID: 0x0ECB (Harman/JBL)
- PID: 0x20A2
- Seri no: yok (0000000000000000)
- Firmware: v0.8.0
- Çipler: dongle Airoha AB1565, kulaklık Airoha AB1568 (RACE cevaplarından, 07_acilis_mekansal)

## Interface'ler
- MI_00: Game ses (çıkış)
- MI_02: Chat ses (çıkış + mikrofon)
- MI_05: HID
  - COL01: vendor-defined 0xFF13 – ana kontrol kanalı (doğrulandı)
  - COL02: vendor-defined 0xFF99 – anlamı bilinmiyor
  - COL03: Telephony / headset (Phone Mute basış atımı; durum 0xFF13'ten okunur)

## Notlar
- Consumer control koleksiyonu yok ve ses scroll'u hiç USB trafiği üretmiyor → ses seviyesi kulaklıkta yerel (06_scroll).
- Game/Chat scroll'u HID'den bildiriliyor (Input 0x10).

## Interface ayrıntıları (UsbTreeView)
- IF0: Game audio control – FU: mute + L/R volume
- IF1: Game streaming – OUT EP 0x01, 48 kHz / 16 bit / stereo
- IF2: Chat audio control – FU: kulaklık mute + L/R volume, mikrofon mute + volume
- IF3: Chat streaming – OUT EP 0x02, 48 kHz / 16 bit / stereo
- IF4: Mikrofon streaming – IN EP 0x81, mono, 16/48 kHz
- IF5: HID – sadece interrupt IN EP 0x83 (64 bayt). Komutlar kontrol kanalından (SET/GET_REPORT).
- Audio control interface'lerinde bildirim uç noktası yok → scroll bilgisi HID'den gelmeli.

## HID Report Descriptor (743 bayt)
- COL01 – Usage Page 0xFF13 (ana kontrol)
  - Input: 0x02-0x10, 0x5C, 0x75 (1 B); 0x05 (20 B); 0x72 (2 B); 0x4C (3 B); 0x4D (7 B); 0x29 (63 B)
  - Output: 0x06 (61 B), 0x23 (1 B), 0x72 (2 B)
  - Feature: 0x45-0x69 (çoğu 1 B), 0x5A/0x61 (16 B), 0x29/0x5B/0x71 (63 B) ...
  - ⚠️ 0xF0-0xFB: muhtemelen firmware/fabrika – ASLA YAZMA
- COL02 – Usage Page 0xFF99: Feature 0x9A (63 B), Input 0x9B (1 bit)
- COL03 – Telephony Headset: Report 0x2F (hook, phone mute, LED'ler)

## Not
- İkinci HID descriptor = "Other Speed Configuration" (USB 1.1 yedek), aynı içerik.