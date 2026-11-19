# JBL Quantum 910P – Özellikler

Bağlantı: yalnızca 2.4 GHz dongle (VID 0x0ECB / PID 0x20A2).
Ayrıntılı cihaz bilgisi için: `device-info.md`

## Fiziksel kontroller

| Kontrol | İşlev | Kapsamda mı? | İletişim |
|---|---|---|---|
| ANC tuşu | Kısa basış: ANC aç/kapa · Uzun basış: TalkThru | Evet | Olay: Input 0x02 · Okuma: Feature 0x45 · Ayar: Feature 0x46 (doğrulandı) |
| Scroll 1 | Ana ses seviyesi | Hayır (okunamıyor) | USB'ye hiç bildirilmiyor, kulaklıkta yerel (06_scroll) |
| Scroll 2 | Game/Chat dengesi | Evet (okuma) | Olay: Input 0x10 · Okuma: Feature 0x62 (00 tam Chat … 10 tam Game, doğrulandı) |
| Mikrofon tuşu | Mikrofonu sessize alır (LED yanar). Kol kalkıkken çalışmaz | Evet (sadece durum okuma) | Olay: Input 0x06 · Okuma: Feature 0x67 (01 açık, 00 sessiz, doğrulandı) |
| Mikrofon kolu (boom) | Kaldırınca mute (LED yanar) | Evet (sadece durum okuma) | Tuşla aynı: Input 0x06 · Feature 0x67 (doğrulandı) |
| Mekânsal ses tuşu | Mekânsal ses modunu değiştirir (ses işleme PC'de, QuantumENGINE) | Evet | Olay: Input 0x72 (sadece tuşla) · Okuma: Feature 0x72 · Ayar: Output 0x72 [72, yeni, önceki] (doğrulandı) |
| Güç mandalı (1x) | Açar, dongle'a bağlanır | Dolaylı | Bağlantı durumu; aday Input 0x03 / 0x09 (henüz görülmedi) |
| Güç mandalı (2x) | Dongle + Bluetooth birlikte | Hayır | Mod değişimi input'u olabilir |
| 3.5 mm jack | Analog ses | Hayır | Yok (USB dışı) |
| USB-C | Şarj | Hayır | Şarj durumu; aday Input 0x03 / 0x09 (henüz görülmedi) |

## ANC tuşu davranışı (02_anc_dizi ile doğrulandı)

- Kapalı    --kısa-->  ANC
- ANC       --kısa-->  Kapalı
- Kapalı / ANC  --uzun-->  TalkThru
- TalkThru  --kısa veya uzun-->  ANC (her zaman)
- Her geçişte tek bir olay paketi geliyor, ara geçiş yok.

## Mekânsal ses modları (read_state.py ile doğrulandı)

- 00 Kapalı
- 01 Açık, sabit (kafa takipsiz)
- 02 Açık, kafa takibi

## Uygulamadan kontrol edilenler

| Özellik | Seçenekler | Kapsamda mı? |
|---|---|---|
| Pil durumu | Yüzde, şarj oluyor mu | Evet |
| Mekânsal ses | Kapalı / sabit / kafa takibi | Evet (kulaklıkta da tuşu var) |
| Mikrofon kazancı | Yüzde | Sonraki sürüm |
| Yan ton (sidetone) | Aç/kapa + seviye | Sonraki sürüm |
| DRC | Aç/kapa | Sonraki sürüm |
| Mikrofon ekolayzırı | Natural / Bright / Powerful | Sonraki sürüm |
| Ekolayzır (kulaklık) | – | Hayır |
| Aydınlatma | – | Hayır |
| Oda boyutu (kafa takibi) | Küçük / Orta / Büyük | Hayır (PC'de işleniyor) |
| Yeniden merkezle | Buton | Sonraki sürüm (Feature 0x5E) |

## Gizli özellikler

- Bağlantı durumu: kulaklık açık/kapalı, dongle takılı ama kulaklık yok

## İlk sürüm kapsamı (özet)

1. Pil durumu
2. ANC / TalkThru / Kapalı (okuma + ayarlama)
3. Mikrofon mute durumu (sadece okuma)
4. Game/Chat dengesi (okuma)
5. Mekânsal ses modu (okuma + ayarlama; ses işleme olmadan duyulur etkisi yok)
6. Bağlantı durumu

Kapsamdan çıkarıldı: ses seviyesi (cihaz USB'ye bildirmiyor, 06_scroll).

## Kontrol edilecekler

- [x] Mikrofon: 0x06'da 01 mi 00 mı "sessiz"? → 00 sessiz, 01 açık; tuş ve kol aynı
- [x] Mekânsal ses: 0x72 mod değerleri → 00 Kapalı, 01 Sabit, 02 Kafa takibi
- [x] Game/Chat: 0x10 değer aralığı → 0x00 tam Chat, 0x08 orta, 0x10 tam Game
- [x] Ses seviyesi: nereden okunuyor? → Okunamıyor, USB'ye bildirilmiyor
- [x] Mekânsal ses nasıl ayarlanıyor? → Output 0x72 [72, yeni, önceki]
- [x] Açılışta ANC ve Game/Chat durumu nasıl öğreniliyor? → Feature 0x45 / Feature 0x62
- [ ] Pil, şarj ve bağlantı durumu: pil bulundu (Feature 0x49 / Input 0x08, tek ölçüm); şarj ve bağlantı → 11 kaydı