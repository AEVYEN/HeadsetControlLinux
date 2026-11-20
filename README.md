# JBL Quantum 910P – Linux kontrol uygulaması

JBL'in QuantumENGINE uygulamasının Linux karşılığı. Protokolü USBPcap + Wireshark ile çözüyoruz.

**Kararlar (2026-11-18):**
- Dil: **Rust**.
- Hedef: **tüm Linux dağıtımları**.
- Geliştirme şimdilik Windows'ta, Linux testleri WSL2 üzerinde yapılacak.
- Kodu kullanıcı yazar, Claude yol gösterir. Çalışma kuralları: [CLAUDE.md](CLAUDE.md)

## Durum
| Özellik | Açılışta okuma | Olay | Ayar | |
|---|---|---|---|---|
| ANC / TalkThru / Kapalı | Feature 0x45 | 0x02 | Feature 0x46 | ✅ |
| Game/Chat | Feature 0x62 | 0x10 | – | ✅ |
| Mikrofon mute | Feature 0x67 | 0x06 | – | ✅ |
| Mekânsal ses modu | Feature 0x72 | 0x72 | Output 0x72 `[72, yeni, önceki]` | ✅ |
| Pil yüzdesi (5'er adım) | Feature 0x49 | 0x08 (değişince kendiliğinden) | – | ✅ |
| Bağlantı durumu | ? | aday 0x03 / 0x09 | – | ⏳ arastirma.md A2 |
| Şarj durumu | ? | aday 0x03 / 0x09 | – | 💤 ertelendi |

- Protokol tamamen Windows + Python + hidapi ile doğrulandı. Bu çalışma `eski-python/` klasöründe arşivlendi.
- Hepsi QuantumEngineService olmadan da çalışıyor.
- Ses seviyesi USB'ye bildirilmiyor, bu yüzden kapsam dışı.
- Mekânsal ses işlemesi PC'de yapılıyor. Linux'ta mod değişir ama duyulur bir etkisi muhtemelen olmaz. Bir çözüm fikri için bkz. arastirma.md C12.

## Dosyalar
- [CLAUDE.md](CLAUDE.md): çalışma anlaşması, kullanıcının talimatları
- [protocol.md](protocol.md): çözülmüş protokol ve **güvenlik kuralları** (ana kaynak)
- [features.md](features.md): özellikler ve sürüm kapsamı
- [device-info.md](device-info.md): USB/HID yapısı
- [arastirma.md](arastirma.md): açık sorular ve sonuçlar
- [yol-haritasi.md](yol-haritasi.md): Rust adımları
- `kayitlar/`: Wireshark kayıtları ve ölçüm logları (aşağıda)
- `descriptors/`: UsbTreeView çıktısı
- `eski-md-dosyalari/`, `eski-python/`: arşiv

## ⚠️ Güvenlik (ayrıntı: protocol.md)
- Yazılabilecek raporlar sadece: Feature 0x46 (ANC), Output 0x72 (mekânsal ses).
- ASLA dokunulmayacaklar: Feature 0xF0–0xFB, Output 0x06 (Airoha RACE kanalı), COL02 0x9A.
- Okuma da sadece resmi uygulamanın okuduğu Feature'larla sınırlı.

## Kayıtlar (`kayitlar/`)
| Dosya | İçerik |
|---|---|
| 00_bosta | Boşta arka plan trafiği |
| 01_anc_kisa_kapali-to-anc, 02_anc_dizi | ANC tuşu olayları |
| 03_bosta_engine_kapali | Uygulama penceresi kapalı |
| 04_anc_uygulamadan, 04_anc_uygulamadan_tamami | Feature 0x46 komutu |
| 05_hizmet_durdurulmus | Hizmet olmadan gelen olaylar |
| 06_scroll | Game/Chat ve ses scroll'u |
| 07_acilis_mekansal | Hizmet açılışı (RACE, Feature okumaları), mekânsal ses tuşu |
| 08_mekansal_uygualamdan | Output 0x72 komutu |
| 09_yazma_hizmetsiz | write_test.py, hizmet kapalı |
| 10_kafa_takibi_ayarlari | Oda boyutu (USB trafiği yok), yeniden merkezle (Feature 0x5E) |
| battery_log.csv | Pil izleme, 2026-11-18 (arastirma.md A1) |

