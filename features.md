# JBL Quantum 910P – Özellikler ve kapsam

Bağlantı: yalnızca 2.4 GHz dongle (VID 0x0ECB / PID 0x20A2). Cihaz ayrıntıları: [device-info.md](device-info.md).
Protokol ayrıntıları: [protocol.md](protocol.md).

## Fiziksel kontroller

| Kontrol | İşlev | Kapsamda mı? | İletişim |
|---|---|---|---|
| ANC tuşu | Kısa basış: ANC aç/kapa · Uzun basış: TalkThru | Evet | Olay 0x02 · Okuma Feature 0x45 · Ayar Feature 0x46 ✅ |
| Scroll 1 | Ana ses seviyesi | Hayır | USB'ye hiç bildirilmiyor, kulaklıkta yerel işleniyor (06_scroll) |
| Scroll 2 | Game/Chat dengesi | Evet (okuma) | Olay 0x10 · Okuma Feature 0x62 (00 tam Chat … 10 tam Game) ✅ |
| Mikrofon tuşu | Mikrofonu sessize alır (LED yanar). Kol kalkıkken çalışmaz | Evet (okuma) | Olay 0x06 · Okuma Feature 0x67 (01 açık, 00 sessiz) ✅ |
| Mikrofon kolu | Kaldırınca mute (LED yanar) | Evet (okuma) | Tuşla aynı: olay 0x06 · Feature 0x67 ✅ |
| Mekânsal ses tuşu | Modu değiştirir (ses işleme PC'de) | Evet | Olay 0x72 (sadece tuşla) · Okuma Feature 0x72 · Ayar Output 0x72 `[72, yeni, önceki]` ✅ |
| Güç mandalı (1x) | Açar, dongle'a bağlanır | Dolaylı | Bağlantı durumu ❓ (arastirma.md A2) |
| Güç mandalı (2x) | Dongle + Bluetooth birlikte | Hayır | – |
| 3.5 mm jack | Analog ses | Hayır | USB dışı |
| USB-C | Şarj | Ertelendi | Şarj durumu ❓ (arastirma.md A3) |

## ANC tuşu davranışı (02_anc_dizi ile doğrulandı ✅)
- Kapalı --kısa--> ANC
- ANC --kısa--> Kapalı
- Kapalı / ANC --uzun--> TalkThru
- TalkThru --kısa veya uzun--> ANC (her zaman)
- Her geçişte tek bir olay paketi geliyor, ara geçiş yok.

> **Not – resmi belgeyle çelişki:** JBL'in 910P destek sayfası "kısa basış ANC'den TalkThru'ya geçirir, uzun basış ANC'yi kapatır" diyor. Bizim kayıtla ölçtüğümüz davranış bunun tersi, **esas alınan bizim ölçümümüz**. Dongle firmware'i v0.8.0. Fark firmware sürümünden ya da 910 / 910P model farkından kaynaklanıyor olabilir.

## Mekânsal ses modları ✅
- 00 Kapalı
- 01 Açık, sabit (kafa takipsiz)
- 02 Açık, kafa takibi

Mekânsal sesi işleyen kısım PC'de (QuantumENGINE). Linux'ta mod değişir ama duyulur bir etkisi muhtemelen olmaz (arastirma.md C12).

## Pil ✅
- Yüzde olarak, **5'er adımla** bildiriliyor (%75 → %70, ara değer yok).
- Değişince kulaklık kendiliğinden 0x08 olayı gönderiyor. Uygulama açılışta bir kez okur, sonra olayı dinler.
- Arayüz: 20 kademeli gösterge yeterli.

## Uygulamadan kontrol edilenler (QuantumENGINE)

| Özellik | Seçenekler | Kapsamda mı? |
|---|---|---|
| Pil durumu | Yüzde, şarj oluyor mu | Evet (yüzde ✅, şarj ertelendi) |
| Mekânsal ses | Kapalı / sabit / kafa takibi | Evet |
| Mikrofon kazancı | Yüzde | Sonraki sürüm (arastirma.md B6) |
| Yan ton (sidetone) | Aç/kapa + seviye | Sonraki sürüm (B6) |
| DRC | Aç/kapa | Sonraki sürüm (B6) |
| Mikrofon ekolayzırı | Natural / Bright / Powerful | Sonraki sürüm (🔶 Feature 0x4C/0x4D/0x4B) |
| Ekolayzır (kulaklık) | – | Hayır |
| Aydınlatma | – | Hayır |
| Oda boyutu (kafa takibi) | Küçük / Orta / Büyük | Hayır (PC'de işleniyor, USB trafiği yok) |
| Yeniden merkezle | Buton | Hayır (Feature 0x5E, yazılmayacak) |

## İlk sürüm kapsamı
1. Pil yüzdesi ✅
2. ANC / TalkThru / Kapalı: okuma + ayarlama ✅
3. Mikrofon mute durumu: sadece okuma ✅
4. Game/Chat dengesi: okuma ✅
5. Mekânsal ses modu: okuma + ayarlama ✅ (ses işleme olmadan duyulur etkisi yok)
6. Bağlantı durumu ❓ (arastirma.md A2)

Kapsam dışı: ses seviyesi (cihaz USB'ye bildirmiyor), şarj durumu (ertelendi).
