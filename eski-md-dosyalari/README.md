# JBL Quantum 910P – Linux kontrol uygulaması

QuantumENGINE'in Linux alternatifi. Windows + VS Code'da geliştiriliyor.
Protokol USBPcap + Wireshark ile çözülüyor; Python 3.14 + hidapi (.venv) ile test ediliyor.
Plan: Python çekirdek → CLI → GUI; Linux'ta hidraw + udev kuralı.

## Dosyalar
- `protocol.md` – çözülmüş protokol, güvenlik kuralları, açık sorular (ana kaynak)
- `features.md` – kulaklığın özellikleri ve ilk sürüm kapsamı
- `device-info.md` – USB/HID yapısı
- `listen.py` – açılışta durumu okur, olayları çözerek dinler (sadece okuma)
- `write_test.py` – ANC ve mekânsal ses yazma testi (izin listeli)
- `list_devices.py` – HID koleksiyonlarını listeler
- `read_state.py` – Feature okuma denemeleri için karalama

## ⚠️ Güvenlik (ayrıntı: protocol.md)
- Yazılabilir sadece: Feature 0x46 (ANC), Output 0x72 (mekânsal ses)
- ASLA yazılmaz: Feature 0xF0–0xFB, Output 0x06 (Airoha RACE kanalı), COL02 0x9A
- Okuma sadece resmi uygulamanın okuduğu Feature'lardan

## İlk sürüm – durum
| Özellik | Açılışta okuma | Olay | Ayar |
|---|---|---|---|
| ANC / TalkThru / Kapalı | Feature 0x45 | Input 0x02 | Feature 0x46 |
| Game/Chat | Feature 0x62 | Input 0x10 | – |
| Mikrofon mute | Feature 0x67 | Input 0x06 | – |
| Mekânsal ses modu | Feature 0x72 | Input 0x72 | Output 0x72 [72, yeni, önceki] |
| Pil yüzdesi | Feature 0x49 | Input 0x08 | – |
| Şarj / bağlantı | ? | aday 0x03 / 0x09 | – |

- Hepsi hizmet (QuantumEngineService) olmadan da çalışıyor.
- Ses seviyesi USB'ye bildirilmiyor → kapsam dışı.
- Mekânsal ses işleme PC'de (QuantumENGINE); Linux'ta mod değişir ama duyulur etkisi muhtemelen yok.

## Kayıtlar (pcapng)
- 00_bosta – boşta arka plan trafiği
- 01_anc_kisa_kapali-to-anc, 02_anc_dizi – ANC tuşu olayları
- 03_bosta_engine_kapali – uygulama penceresi kapalı
- 04_anc_uygulamadan_4adim / _tamami – Feature 0x46 komutu
- 05_hizmet_durdurulmus – hizmet olmadan olaylar
- 06_scroll – Game/Chat ve ses scroll'u
- 07_acilis_mekansal – hizmet açılışı (RACE, Feature okumaları), mekânsal ses tuşu
- 08_mekansal_uygulamadan – Output 0x72 komutu
- 09_yazma_hizmetsiz – write_test.py, hizmet kapalı
- 10_kafa_takibi_ayarlari – oda boyutu (USB trafiği yok), yeniden merkezle (Feature 0x5E)

## Sıradaki adım
11_guc_sarj.pcapng (hizmet ve uygulama açık, listen.py açık, 10 sn aralıklarla):
kulaklığı kapat → aç → şarj kablosunu tak → çıkar. Hedef: 0x03 / 0x09, şarj ve bağlantı durumu.
Ayrıca: pil farklı bir seviyedeyken 0x49'u tekrar oku (5'er mi bildiriliyor?).
Sonra: Python çekirdek kütüphanesi.