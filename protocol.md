# JBL Quantum 910P – Protokol Notları

Etiketler: ✅ doğrulandı · 🔶 hipotez · ❓ bilinmiyor.
Kaynak kayıtların hepsi `kayitlar/` klasöründe. Açık sorular: [arastirma.md](arastirma.md)

## ⚠️ Güvenlik kuralları

- Feature **0xF0, 0xF1, 0xF4, 0xF5, 0xF6, 0xFA, 0xFB**'ye ASLA yazılmaz, bunlar okunmaz da.
  - Muhtemelen firmware güncelleme ya da bakım raporları.
  - Yanlış veri kulaklığı veya dongle'ı kalıcı olarak kullanılamaz hale getirebilir.
- **Output 0x06**'ya (RACE komut kanalı) ASLA yazılmaz.
  - Bu kanal cihazın iç ayar belleğine erişiyor. Bu tür protokollerde belleğe yazan ve firmware güncelleyen komutlar da bulunur.
  - Dikkat: **Input 0x06** aynı ID'yi taşır ama zararsızdır, mikrofon olayıdır.
- **COL02 Feature 0x9A** (63 B): anlamı bilinmiyor, yazılmaz.
- Sadece resmi uygulamanın kaydıyla doğrulanmış raporlara yazılır. Şu an yazılabilenler: **Feature 0x46** ve **Output 0x72**.
- Bilinmeyen bir rapora deneme amaçlı değer gönderilmez. Önce resmi uygulamanın ne gönderdiği kaydedilir.
- Okuma için de aynı kural geçerli: sadece resmi uygulamanın kendisinin okuduğu Feature'lar okunur.
- Kodda da aynı kural uygulanır:
  - Yazma fonksiyonu sadece izin listesindeki Report ID ve değerleri kabul eder.
  - Yasaklı raporlar ayrıca açıkça listelenir. İzin listesiyle çakışırsa program başlamaz.
  - Bunun Python örneği: `eski-python/quantum910p/protocol.py` (`WRITABLE`, `FORBIDDEN`).

## Genel
- Olaylar (cihaz → PC): interrupt IN, EP 0x83. Format: `[Report ID][değer...]`.
- Komutlar (PC → cihaz): kontrol kanalı, SET_REPORT (bmRequestType 0x21, bRequest 0x09), interface 5.
- Rapor uzunlukları descriptor'dan alınır (bkz. Rapor haritası).
  - hidapi Windows'ta her paketi 64 bayta tamamlıyor. Interrupt okumada fazlası eski veridir, kırpılmalı.
  - İstisna: GET_REPORT 0x07 (RACE cevabı).
  - Linux'ta (hidraw) bu davranış farklı olabilir, bkz. arastirma.md C7.
- Telephony koleksiyonu (COL03), Report 0x2F:
  - bit0 Hook Switch, bit1 Phone Mute (Relative = basış atımı, durum değil), bit7 Button 1.
  - Output 0x2F: LED'ler (Off-Hook, Mute, Ring, Hold, Microphone, On-Line).
- COL02 (0xFF99): Feature 0x9A (63 B), Input 0x9B (1 bit, Relative). ❓ Anlamı bilinmiyor.
- ✅ Bütün olaylar ve iki yazma komutu QuantumEngineService **olmadan** da çalışıyor (05_hizmet_durdurulmus, 09_yazma_hizmetsiz).

## Olaylar (Input, cihaz → PC)

### 0x02 – Ortam sesi modu ✅
| Değer | Anlamı |
|---|---|
| 0x00 | Kapalı |
| 0x01 | ANC |
| 0x02 | TalkThru |

- Kulaklıktaki tuşla her mod değişikliğinde tek bir olay geliyor, ara geçiş yok.
- Feature 0x46 komutundan sonra onay olarak da geliyor (70–500 ms).
- Kaynak: 01_anc_kisa_kapali-to-anc, 02_anc_dizi, 03_bosta_engine_kapali

### 0x10 – Game/Chat dengesi ✅
- 1 B. Aralık: 0x00 = tam Chat, 0x08 = orta, 0x10 = tam Game. Toplam 17 kademe.
- Olaylar yaklaşık 220 ms'de bir seyreltilmiş geliyor. Ara değerler atlanabiliyor, son değer her zaman geliyor.
- Cihaz bağlanınca mevcut konumu kendiliğinden göndermiyor. Açılışta Feature 0x62 okunmalı.
- Kaynak: 06_scroll

### 0x08 – Pil yüzdesi ✅
- 1 B, doğrudan yüzde değeri: 0x32 = %50, 0x4B = %75, 0x46 = %70.
- ✅ **5'er adımla bildiriliyor.** 91 dakika boyunca hep %75 okundu. Sonra değer ara değerlere uğramadan doğrudan %70 oldu.
- ✅ **Değişince kendiliğinden geliyor.** 19:57:58'de `08 46` geldi: önceki okumadan 61 sn sonra, sonrakinden 58 sn önce.
- ✅ **Feature 0x49 okuması bu olayı tetikliyor.** 2026-11-18'de 47 okumanın 47'sinde, ~1 sn içinde geldi. Önceki kayıtlarda da (07_acilis_mekansal, listen.py) aynısı görüldü.
- Boşta periyodik bir pil bildirimi yok. 00_bosta kaydında 51 sn boyunca hiç olay gelmedi.
- **Uygulama tasarımı:** Açılışta Feature 0x49 bir kez okunur, sonra sadece 0x08 olayı dinlenir. Yoklama (polling) gerekmez.
- Kaynak: kayitlar/battery_log.csv (2026-11-18), 07_acilis_mekansal

### 0x06 – Mikrofon durumu ✅
| Değer | Anlamı |
|---|---|
| 0x00 | Sessiz |
| 0x01 | Açık |

- Tuş ve mikrofon kolu aynı olayı üretiyor. Kodlama Feature 0x67 ile aynı.
- Kol kalkıkken tuş yok sayılıyor: LED değişmiyor, olay gelmiyor.
- ⚠️ Aynı ID'nin Output yönü RACE kanalı, oraya ASLA yazılmaz.
- Kaynak: listen.py

### 0x72 – Mekânsal ses modu ✅
| Değer | Anlamı |
|---|---|
| 0x00 | Kapalı |
| 0x01 | Açık, sabit (kafa takipsiz) |
| 0x02 | Açık, kafa takibi |

- 2 B: `[mod, FF]`
- Sadece kulaklıktaki mekânsal ses tuşuyla geliyor. Tuş sırası: 01 → 02 → 00 → 01.
- Uygulamadan (Output 0x72) mod değiştirildiğinde bu olay **gelmiyor**.
- Kaynak: 07_acilis_mekansal, 08_mekansal_uygualamdan. Değerler Feature 0x72 okumasıyla da doğrulandı.

### 0x05 – Kafa takibi akışı ✅
- 20 B.
  - Bayt 3–6: uint32 zaman damgası (ms).
  - Bayt 11–18: 4×int16 quaternion (Q14, /16384, norm = 1).
- Sadece mekânsal ses modu 02 (kafa takibi) iken geliyor, saniyede ~100 paket.
- Hizmet çalışmıyorken gelmedi (09_yazma_hizmetsiz).
- ✅ Akışı başlatan özel bir komut yok. 07'de kulaklık tuşuyla mod 02'ye geçildikten 95 ms sonra kendiliğinden başladı. Arada hizmetten sadece `23 00` kalp atışı gitti.
- 🔶 Kulaklığın akış için aradığı koşul ya açık Game ses akışı (EP 0x01) ya da `23 00` kalp atışı olabilir. Bkz. arastirma.md B5.
- Uygulama bu akışı yok sayabilir.
- Kaynak: 07_acilis_mekansal

### 0x04 – Yeniden merkezleme bitti? 🔶
- `04 FF`: Feature 0x5E komutundan ~0,7 sn sonra geldi.
- Kaynak: 10_kafa_takibi_ayarlari

### 0x07 (olay), 0x5C, 0x75 – ❓
- `07 00`: hizmet açılışında 2 kez geldi. 1 B olay, RACE cevabıyla ilişkisi belirsiz.
- `5C 00`, `75 06`: hizmet açılışında birer kez geldi.
- Kaynak: 07_acilis_mekansal

### 0x03, 0x09 – henüz görülmedi
- 1'er bayt. Şarj ve bağlantı durumu için adaylar.
- 91 dakikalık pil izlemesi boyunca da gelmedi.

### Ses seviyesi – okunamaz ✅
- Ses scroll'u hiç USB trafiği üretmiyor: interrupt olayı yok, 0x07 yanıtı değişmiyor, ses arayüzüne istek gitmiyor.
- Ses seviyesi kulaklıkta yerel olarak işleniyor, PC'den okunamaz.
- Kaynak: 06_scroll

## Açılışta durum okuma (Feature, GET_REPORT)

| Feature | Uzunluk (ID dahil) | Değer | Anlamı |
|---|---|---|---|
| 0x45 | 2 | 00 / 01 / 02 | ✅ ANC durumu (0x02 olayıyla aynı kodlama) |
| 0x49 | 2 | yüzde | ✅ Pil (okuma 0x08 olayını da tetikler) |
| 0x62 | 2 | 00 … 10 | ✅ Game/Chat |
| 0x67 | 2 | 00 / 01 | ✅ Mikrofon: 01 açık, 00 sessiz |
| 0x72 | 3 | 00 / 01 / 02, FF | ✅ Mekânsal ses |
| 0x47, 0x4A, 0x5C | 2 | 00 | ❓ ANC, Game/Chat ve mikrofonla değişmiyor |
| 0x68 | 2 | 01 | ❓ değişmedi |
| 0x75 | 2 | 06 | ❓ değişmedi |
| 0x51 | 13 | 00 08 00 00 05 00 00 06 00 00 08 00 | ❓ |

İşe yaramayan okumalar ❌:
- Input 0x10 → hep `10 00`
- Input 0x02 → hep `02 00`
- Input 0x06 → hep `06 00`
- Feature 0x46 → hep `46 00`, ANC durumunu yansıtmıyor

- Kaynak: read_state.py, 07_acilis_mekansal
- ✅ 2026-11-18'de beş Feature birlikte okundu (`read_state()`), değerler kulaklıktaki durumla tutarlıydı.

## Komutlar (PC → cihaz)

### Feature 0x46 – Ortam sesi modunu ayarla ✅
- SET_REPORT, Feature, Report ID 0x46, interface 5.
- Veri: `[0x46, değer]`. Değerler: 0x00 Kapalı, 0x01 ANC, 0x02 TalkThru.
- Kulaklık 70–500 ms içinde 0x02 olayıyla onaylıyor. Linux'ta ~1 sn zaman aşımı kullanılmalı.
- Gerçek durum Feature 0x45'ten okunur. Feature 0x46 okuması hep 00 döner.
- Uygulamadaki "hatırlanan mod" uygulama tarafında tutuluyor, cihaz sadece son değeri alıyor.
- Hizmet olmadan da çalışıyor (09_yazma_hizmetsiz, write_test.py).
- Kaynak: 04_anc_uygulamadan, 04_anc_uygulamadan_tamami

### Output 0x72 – Mekânsal ses modunu ayarla ✅
- SET_REPORT, Output (wValue 0x0272), Report ID 0x72, interface 5.
- Veri: `[0x72, yeni mod, önceki mod]`.
  - Örnekler: `72 01 00` (Kapalı→Sabit), `72 02 01` (Sabit→Kafa takibi), `72 00 02` (Kafa takibi→Kapalı).
  - Üçüncü bayt FF değil, önceki mod. Neden gerektiği bilinmiyor, bu yüzden uygulama birebir taklit edilir: önce Feature 0x72'den mevcut mod okunur, sonra `[72, yeni, mevcut]` gönderilir.
- **Onay olayı yok.** Onay için komuttan sonra Feature 0x72 tekrar okunur, yeni değeri hemen gösteriyor.
- Kafa takibine geçişte 0x05 akışı ~150 ms sonra başlıyor, kapatınca ~80 ms sonra duruyor. Bu, hizmet açıkken böyle.
- Hizmet olmadan da çalışıyor (09_yazma_hizmetsiz).
- Kaynak: 08_mekansal_uygualamdan

### Feature 0x5E – Kafa takibini yeniden merkezle (gözlendi, YAZILMAYACAK, kapsam dışı)
- SET_REPORT, Feature, veri: `[0x5E, 0x00]`. Uygulamadaki "Yeniden merkezle" butonu gönderiyor.
- Etkisi:
  - 0x05 akışı ~0,3 sn duruyor.
  - Ardından `04 FF` geliyor.
  - Akış sıfırlanmış yönle devam ediyor (quaternion'un iki bileşeni ~0).
- Kaynak: 10_kafa_takibi_ayarlari

### Uygulamanın açılışta yazdığı Feature'lar (bilgi amaçlı, YAZILMAYACAK)
- Feature 0x4C (3 B), ardından 0x4D (7 B) grupları. Toplam 3 grup, 4 + 4 + 3 giriş:
  - `4C [00 64 04]` → 4× `4D [00, 0..3, ...]`
  - `4C [01 64 04]` → 4× `4D [01, 0..3, ...]`
  - `4C [02 64 03]` → 3× `4D [02, 0..2, ...]`
- Ardından Feature 0x4B = 00.
- 🔶 Mikrofon ekolayzırı ön ayarları olabilir: 3 grup = Natural / Bright / Powerful, sonuncusu da seçili ön ayar.
- Kaynak: 07_acilis_mekansal

## RACE komut kanalı (Output 0x06 / Input 0x07) – ⚠️ sadece bilgi amaçlı
- Airoha çipleri: dongle "AB1565", kulaklık "AB1568_dual_chip". Bu adlar RACE cevaplarından okundu.
- Airoha RACE protokolüne uyuyor:
  - Komut `05 5A`, cevap `05 5B`.
  - Ardından uzunluk (2 B LE) ve komut kodu (2 B LE).
- Komut: SET_REPORT Output 0x06, 62 B: `[06, uzunluk, hedef, 05 5A, uzunluk16, kod16, veri...]`
- Cevap: GET_REPORT Input 0x07, 64 B: `[07, uzunluk, bayrak, 05 5B, uzunluk16, kod16, durum, veri...]`
- 🔶 Hedef baytı: 00 → dongle (AB1565 cevap verdi), 80 → kulaklık (AB1568 cevap verdi).
- 🔶 Kod 0x0A0C: iç ayar belleğinden anahtar okuma.
  - Örnek: veri `02 10 E8 03` → 0x1002 anahtarı okunuyor, cevap "AB1565".
  - Hizmetin açılışta okuduğu anahtarlar: 0x1002, 0x1001, 0xF2B0, 0xF233, 0xF234, 0xEF00, 0xEF10.
- Diğer görülen kodlar: 0x2C80, 0x0CC4, 0x0D00, 0x0901. ❓ Anlamları bilinmiyor.
- Cevap yokken 0x07 tamponda son cevabın artığını döndürüyor (uzunluk baytı 00). Eskiden "sabit 0x07 cevabı" ve "44 AC = 44100" sanılan şeyler bu artıktan ibaret.
- 🔶 Feature 0x29 (63 B) okuması da aynı tampon içeriğini döndürüyor gibi.
- ⚠️ Kendi kodumuzdan bu kanala komut **gönderilmez**.
- Kaynak: 07_acilis_mekansal

## Arka plan trafiği (QuantumEngineService)
- GET_REPORT Input 0x07, ~4,5 ms aralıkla, 64 B. RACE cevabı bekliyor.
- SET_REPORT Output 0x23, değer 00, 1 sn aralıkla. 🔶 Kalp atışı olabilir.
- Bu trafiği uygulama penceresi değil, Windows hizmeti (QuantumEngineService) üretiyor. Pencere kapalıyken de sürüyor.
- Hizmet başlarken şunları yapıyor:
  - Ses arayüzünü açıyor (SET_INTERFACE 1/1, 48000 Hz).
  - RACE sorguları gönderiyor.
  - Feature okumaları yapıyor.
  - Feature 0x4C / 0x4D / 0x4B'ye yazıyor.
- Hizmet çalışırken Game ses çıkışı (EP 0x01) sürekli açık tutuluyor. Hizmet durunca akış da duruyor.
- Hizmet durunca 0x07 sorgusu ve 0x23 kalp atışı tamamen kesiliyor, olaylar yine de gelmeye devam ediyor.

## Mekânsal ses nerede işleniyor? ✅ PC'de
- Game USB çıkışı donanımda sadece 2 kanal, 48 kHz (descriptor).
- Windows'ta Game hoparlörü 7.1'e çekilince çalışıyor. Yani Windows tarafında sanal bir 7.1 işleyici var.
- Oda boyutu değişikliği hiç USB trafiği üretmiyor (10_kafa_takibi_ayarlari).
- Kulaklıkta yapılan tek iş kafa açısını ölçmek (0x05) ve yeniden merkezlemek (0x5E).
- Linux için sonuç: 0x72 komutu modu değiştirir ama ses işleyici olmadan duyulur bir etkisi muhtemelen yoktur. Bkz. arastirma.md C12.

## Rapor haritası (descriptor, COL01 0xFF13; uzunluk Report ID hariç)
| Tür | Report ID (uzunluk) |
|---|---|
| Sadece Input | 02, 03, 04, 07, 08, 09, 10 (1'er); 05 (20) |
| Input + Output | 06 (Input 1, Output 61 = RACE komutu ⚠️) |
| Input + Feature | 29 (63), 4C (3), 4D (7), 5C (1), 75 (1) |
| Input + Output + Feature | 72 (2) |
| Sadece Output | 23 (1) |
| Sadece Feature | 45, 46, 47, 49, 4A, 4B, 4E, 4F, 53, 59, 5D–60, 62–69, 6F (1'er); 50, 52 (2); 51 (12); 5A, 61 (16); 5B, 71 (63) |
| ⚠️ Feature, ASLA DOKUNMA | F0, F1, F6 (1); F5 (5); FA (12); F4, FB (63) |
