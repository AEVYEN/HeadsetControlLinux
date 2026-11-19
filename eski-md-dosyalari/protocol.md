# JBL Quantum 910P – Protokol Notları

## ⚠️ Güvenlik kuralları

- Feature 0xF0, 0xF1, 0xF4, 0xF5, 0xF6, 0xFA, 0xFB'ye ASLA yazılmaz.
  Muhtemelen firmware güncelleme / bakım raporları. Yanlış veri kulaklığı veya dongle'ı
  kalıcı olarak kullanılamaz hale getirebilir. Okuma da yapılmaz.
- Output 0x06'ya (RACE komut kanalı) ASLA yazılmaz. Bu kanal cihazın iç ayar belleğine
  erişiyor; bu tür protokollerde belleğe yazan ve firmware güncelleyen komutlar da bulunur.
- COL02 Feature 0x9A (63 B): anlamı bilinmiyor → yazılmaz.
- Sadece anlamı resmi uygulamanın kaydıyla doğrulanmış raporlara yazılır.
    Şu an yazılabilir: Feature 0x46, Output 0x72.
- Bilinmeyen bir rapora deneme amaçlı değer gönderilmez. Önce uygulamanın gönderdiği kaydedilir.
- Okuma için de kural: sadece resmi uygulamanın kendisinin okuduğu Feature'lar okunur.
- Kodda da aynı kural: yazma fonksiyonu sadece izin listesindeki Report ID'leri kabul eder.

## Genel
- Olaylar (cihaz → PC): interrupt IN, EP 0x83, format: [Report ID][değer...]
- Komutlar (PC → cihaz): kontrol kanalı, SET_REPORT (bmRequestType 0x21, bRequest 0x09), interface 5
- Rapor uzunlukları descriptor'dan alınır (bkz. Rapor haritası). hidapi Windows'ta 64 B döndürüyor; interrupt okumada fazlası eski veri.
  İstisna: GET_REPORT 0x07 (RACE cevabı, bkz. RACE komut kanalı).
- Telephony koleksiyonu (COL03), Report 0x2F: bit0 Hook Switch, bit1 Phone Mute (Relative = basış atımı, durum değil), bit7 Button 1.
  Output 0x2F: LED'ler (Off-Hook, Mute, Ring, Hold, Microphone, On-Line).
- COL02 (0xFF99): Feature 0x9A (63 B), Input 0x9B (1 bit, Relative). Anlamı bilinmiyor.

## RACE komut kanalı (Output 0x06 / Input 0x07)
- Airoha çipleri: dongle "AB1565", kulaklık "AB1568_dual_chip" (RACE cevaplarından okundu).
- Airoha RACE protokolüne uyuyor: komut 05 5A, cevap 05 5B, ardından uzunluk (2 B LE) ve komut kodu (2 B LE).
- Komut:  SET_REPORT Output 0x06, 62 B: [06, uzunluk, hedef, 05 5A, uzunluk16, kod16, veri...]
- Cevap:  GET_REPORT Input 0x07, 64 B: [07, uzunluk, bayrak, 05 5B, uzunluk16, kod16, durum, veri...]
- Hedef baytı: 00 → dongle (AB1565 cevap verdi), 80 → kulaklık (AB1568 cevap verdi) (hipotez)
- Kod 0x0A0C: iç ayar belleğinden anahtar okuma (hipotez).
  Örnek: veri 02 10 E8 03 → anahtar 0x1002 okunuyor, cevap "AB1565".
  Hizmetin açılışta okuduğu anahtarlar: 0x1002, 0x1001, 0xF2B0, 0xF233, 0xF234, 0xEF00, 0xEF10
- Diğer görülen kodlar: 0x2C80, 0x0CC4, 0x0D00, 0x0901 (anlamı bilinmiyor)
- Cevap yokken 0x07 tamponda son cevabın artığını döndürüyor (uzunluk baytı 00).
  Önceki notlardaki "sabit 0x07 cevabı" ve "44 AC = 44100" bu artıktan ibaret.
- Feature 0x29 (63 B) okuması da aynı tampon içeriğini döndürüyor gibi (hipotez).
- Kaynak: 07_acilis_mekansal
- ⚠️ Kendi kodumuzdan bu kanala komut gönderilmez (bkz. Güvenlik kuralları).

## Arka plan trafiği (QuantumEngineService)
- GET_REPORT Input 0x07, ~4.5 ms aralıkla, 64 B → RACE cevabı bekliyor (bkz. RACE komut kanalı)
- SET_REPORT Output 0x23, değer 00, 1 sn aralıkla (kalp atışı?)
- Bu trafiği QuantumENGINE penceresi değil, QuantumEngineService (Windows hizmeti) yapıyor.
  Pencere kapalıyken de sürüyor.
- Hizmet başlarken: ses arayüzünü açıyor (SET_INTERFACE 1/1, örnekleme hızı 48000 Hz), RACE sorguları,
  Feature okumaları (bkz. Açılışta durum okuma), Feature 0x4C / 0x4D / 0x4B yazma
- Boşta 51 sn boyunca hiç interrupt olayı yok → periyodik pil bildirimi yok
- Olay paketleri (0x02) uygulama penceresinden bağımsız geliyor
- Hizmet çalışırken Game ses çıkışı (EP 0x01) sürekli açık tutuluyor; hizmet durunca akış da duruyor.

## Olaylar

### Report 0x02 – Ortam sesi modu (doğrulandı)
| Değer | Anlamı |
|---|---|
| 0x00 | Kapalı |
| 0x01 | ANC |
| 0x02 | TalkThru |

- Kulaklıktaki tuşla her mod değişikliğinde tek bir olay geliyor, ara geçiş yok.
- Kaynak: 01_anc_kisa_kapali-to-anc, 02_anc_dizi, 03_bosta_engine_kapali

### Report 0x10 – Game/Chat dengesi (doğrulandı)
- 1 B. Aralık 0x00 = tam Chat, 0x10 = tam Game, orta 0x08, 17 kademe.
- Olaylar yaklaşık 220 ms'de bir seyreltilmiş geliyor, ara değerler atlanabiliyor; son değer her zaman geliyor.
- Cihaz bağlanınca mevcut konumu kendiliğinden göndermiyor.
- Kaynak: 06_scroll

### Report 0x08 – Pil yüzdesi (eşleşti, tek ölçüm)
- Feature 0x49 okunduktan hemen sonra geldi (07_acilis_mekansal, listen.py, 2026-11-18 quantum910p ile tekrar: 08 4B) → okuma tetikliyor olabilir (hipotez, 3 gözlem)
- Ölçümler: 0x32 = %50 (2026-09), 0x4B = %75 (2026-11-18) – ikisi de 5'in katı
- 1 B, doğrudan yüzde: 0x32 = %50 (uygulama %50 gösteriyordu)
- Hizmet açılışında kendiliğinden geldi. Değişince gelip gelmediği henüz bilinmiyor.
- Uygulama pili 5'in katları olarak gösteriyor: cihaz mı 5'er bildiriyor, uygulama mı yuvarlıyor? → farklı seviyede bakılacak
- Kaynak: 07_acilis_mekansal

### Report 0x06 – Mikrofon durumu (doğrulandı)
| Değer | Anlamı |
|---|---|
| 0x00 | Sessiz |
| 0x01 | Açık |

- Tuş ve kol aynı olayı üretiyor (Feature 0x67 ile aynı kodlama).
- Kol kalkıkken tuş yok sayılıyor: LED değişmiyor, olay gelmiyor.
- Kaynak: listen.py

### Report 0x72 – Mekânsal ses modu (doğrulandı)
| Değer | Anlamı |
|---|---|
| 0x00 | Kapalı |
| 0x01 | Açık, sabit (kafa takipsiz) |
| 0x02 | Açık, kafa takibi |
- Uygulamadan (Output 0x72) değişince olay gelmiyor (08_mekansal_uygulamadan).

- 2 B: [mod, FF]
- Kulaklıktaki mekânsal ses tuşuyla geliyor. Tuş sırası: 01 → 02 → 00 → 01.
- Uygulamadan (Output 0x72) değişince olay gelmiyor (08_mekansal_uygulamadan).
- Kaynak: 07_acilis_mekansal; değerler read_state.py (Feature 0x72 okuma) ile de doğrulandı

### Report 0x05 – Kafa takibi akışı
- 20 B. Bayt 3–6: uint32 zaman damgası (ms). Bayt 11–18: 4×int16 quaternion (Q14, /16384, norm = 1).
- Sadece mekânsal ses modu 02 (kafa takibi) iken geliyor, saniyede ~100 paket.
- Uygulama yok sayabilir.
- Kaynak: 07_acilis_mekansal
- Hizmet çalışmıyorken gelmedi (09_yazma_hizmetsiz)

### Report 0x04 – Yeniden merkezleme bitti? (hipotez)
- 04 FF: Feature 0x5E komutundan ~0,7 sn sonra geldi
- Kaynak: 10_kafa_takibi_ayarlari

### Report 0x07 (olay), 0x5C, 0x75 – anlamı bilinmiyor
- 07 00: hizmet açılışında 2 kez geldi (1 B olay; RACE cevabıyla ilişkisi belirsiz)
- 5C 00, 75 06: hizmet açılışında birer kez geldi
- Kaynak: 07_acilis_mekansal

### Henüz görülmeyen Input raporları
- 0x03, 0x09 (1'er B): şarj / bağlantı adayları

### Ses seviyesi
- Ses scroll'u hiç USB trafiği üretmiyor: interrupt olayı yok, 0x07 yanıtı değişmiyor, ses arayüzüne istek yok.
- Kulaklıkta yerel işleniyor → PC'den okunamaz.
- Kaynak: 06_scroll

## Mekânsal ses nerede işleniyor?
- PC'de, QuantumENGINE hizmetinde:
  - Game USB çıkışı donanımda sadece 2 kanal, 48 kHz (descriptor)
  - Windows'ta Game hoparlörü 7.1'e çekilince çalışıyor → Windows tarafında sanal 7.1 işleyici var
  - Oda boyutu değişikliği hiç USB trafiği üretmiyor (10_kafa_takibi_ayarlari)
  - 0x05 akışı hizmet yokken gelmiyor (09_yazma_hizmetsiz)
- Kulaklıkta yapılan tek iş: kafa açısı ölçümü (0x05) ve yeniden merkezleme (Feature 0x5E)
- Linux sonucu: 0x72 modu değiştiriyor ama ses işleyici olmadan duyulur etkisi muhtemelen yok

## Açılışta durum okuma

### Doğrulanan / elenen yöntemler
| Yöntem | Sonuç |
|---|---|
| GET_REPORT Feature 0x72 | ✅ Gerçek mekânsal ses modu: [72, mod, FF] |
| GET_REPORT Feature 0x67 | ✅ Mikrofon: 01 açık, 00 sessiz (tuş ve kol aynı) |
| GET_REPORT Feature 0x49 | ✅ Pil yüzdesi (0x32 = %50, tek ölçüm) |
| GET_REPORT Feature 0x45 | ✅ ANC durumu: 00 Kapalı, 01 ANC, 02 TalkThru |
| GET_REPORT Feature 0x62 | ✅ Game/Chat: 00 tam Chat, 08 orta, 10 tam Game |
| GET_REPORT Input 0x10 | ❌ Hep 10 00 (tam Game'de de) |
| GET_REPORT Input 0x02 | ❌ Hep 02 00 |
| GET_REPORT Input 0x06 | ❌ Hep 06 00 |
| GET_REPORT Feature 0x46 | ❌ Hep 46 00, ANC durumunu yansıtmıyor |

- Kaynak: read_state.py, 07_acilis_mekansal

### Uygulamanın açılışta okuduğu Feature'lar
| Feature | Değer | Anlamı |
|---|---|---|
| 0x45 | 00 / 01 / 02 | ANC durumu ✅ |
| 0x49 | 32 | Pil yüzdesi (%50) ✅ |
| 0x62 | 00 … 10 | Game/Chat ✅ |
| 0x72 | 00 / 01 / 02, FF | Mekânsal ses ✅ |
| 0x67 | 00 / 01 | Mikrofon: 01 açık, 00 sessiz ✅ |
| 0x47, 0x4A, 0x5C | 00 | ANC, Game/Chat ve mikrofonla değişmiyor; ? |
| 0x68 | 01 | ? (değişmedi) |
| 0x75 | 06 | ? (değişmedi) |
| 0x51 (12 B) | 00 08 00 00 05 00 00 06 00 00 08 00 | ? |

- Kaynak: 07_acilis_mekansal, read_state.py

## Komutlar

### Feature 0x46 – Ortam sesi modunu ayarla (doğrulandı)
- Mevcut durum Feature 0x45'ten okunur (aynı kodlama)
- SET_REPORT, Feature, Report ID 0x46, interface 5
- Veri: [0x46, değer]
- Değerler: 0x00 Kapalı, 0x01 ANC, 0x02 TalkThru (0x02 olayıyla aynı kodlama)
- Kulaklık 70-500 ms içinde 0x02 olayıyla onaylıyor → Linux'ta ~1 sn zaman aşımı kullan
- Hizmet olmadan da çalışıyor (09_yazma_hizmetsiz, write_test.py)
- Uygulamadaki "hatırlanan mod" uygulama tarafında tutuluyor; cihaz sadece son değeri alıyor
- Okuma (GET_REPORT Feature 0x46) gerçek durumu vermiyor, hep 00 dönüyor
- Kaynak: 04_anc_uygulamadan_4adim, 04_anc_uygulamadan_tamami, read_state.py

### Output 0x72 – Mekânsal ses modunu ayarla (doğrulandı)
- Hizmet olmadan da çalışıyor; Feature 0x72 komuttan hemen sonra yeni değeri gösteriyor (09_yazma_hizmetsiz)
- Hizmet yokken kafa takibi modunda 0x05 akışı GELMEDİ (1,5 sn) → kafa takibi PC tarafında hizmetle işleniyor olabilir (hipotez)
- SET_REPORT, Output (wValue 0x0272), Report ID 0x72, interface 5
- Veri: [0x72, yeni mod, önceki mod]
  - Örnekler: 72 01 00 (Kapalı→Sabit), 72 02 01 (Sabit→Kafa takibi), 72 00 02 (Kafa takibi→Kapalı)
  - Üçüncü bayt FF değil, önceki mod. Önemi bilinmiyor → uygulamayı birebir taklit et:
    önce Feature 0x72'den mevcut modu oku, sonra [72, yeni, mevcut] gönder
- Onay olayı YOK: uygulamadan değişince 0x72 olayı gelmiyor (olay sadece kulaklık tuşuyla geliyor)
  → onay için komuttan sonra Feature 0x72'yi tekrar oku
- Kafa takibine geçişte 0x05 akışı ~150 ms sonra başlıyor, kapatınca ~80 ms sonra duruyor
- Kaynak: 08_mekansal_uygulamadan
### Feature 0x5E – Kafa takibini yeniden merkezle (gözlendi, YAZILMAYACAK – kapsam dışı)
- SET_REPORT, Feature, veri: [0x5E, 0x00]
- Uygulamadaki "Yeniden merkezle" butonu gönderiyor
- Etkisi: 0x05 akışı ~0,3 sn duruyor, ardından Input 0x04 = FF geliyor,
  akış sıfırlanmış yönle (quaternion'un iki bileşeni ~0) devam ediyor → sıfırlama kulaklıkta yapılıyor
- Kaynak: 10_kafa_takibi_ayarlari

### Uygulamanın açılışta yazdığı Feature'lar (bilgi amaçlı, YAZILMAYACAK)
- Feature 0x4C (3 B) + ardından 0x4D (7 B) grupları: 3 grup, 4 + 4 + 3 giriş
  - 4C [00 64 04] → 4× 4D [00, 0..3, ...]
  - 4C [01 64 04] → 4× 4D [01, 0..3, ...]
  - 4C [02 64 03] → 3× 4D [02, 0..2, ...]
- Ardından Feature 0x4B = 00
- Hipotez: mikrofon ekolayzırı ön ayarları (Natural / Bright / Powerful = 3 grup) ve seçili ön ayar
- Kaynak: 07_acilis_mekansal

## Rapor haritası (descriptor, COL01 0xFF13; uzunluk Report ID hariç)
| Tür | Report ID (uzunluk) |
|---|---|
| Sadece Input | 02, 03, 04, 07, 08, 09, 10 (1'er); 05 (20) |
| Input + Output | 06 (Input 1, Output 61 = RACE komutu ⚠️) |
| Input + Feature | 29 (63), 4C (3), 4D (7), 5C (1), 75 (1) |
| Input + Output + Feature | 72 (2) |
| Sadece Output | 23 (1) |
| Sadece Feature | 45, 46, 47, 49, 4A, 4B, 4E, 4F, 53, 59, 5D–60, 62–69, 6F (1'er); 50, 52 (2); 51 (12); 5A, 61 (16); 5B, 71 (63) |
| ⚠️ Feature, ASLA YAZMA | F0, F1, F6 (1); F5 (5); FA (12); F4, FB (63) |

## Açık sorular
- [x] Hizmet olmadan olaylar geliyor mu? → EVET (05_hizmet_durdurulmus).
      Hizmet durunca 0x07 sorgusu ve 0x23 kalp atışı tamamen duruyor, 0x02 olayı yine geliyor.
- [x] Hizmet olmadan Feature 0x46 ve Output 0x72 çalışıyor mu? → EVET (09_yazma_hizmetsiz)
- [x] Mekânsal ses nasıl ayarlanıyor? → Output 0x72: [72, yeni, önceki] (08_mekansal_uygulamadan)
- [x] Mekânsal ses nerede işleniyor? → PC'de (10_kafa_takibi_ayarlari, 7.1 gereksinimi)
- [ ] 0x04 FF gerçekten "merkezleme bitti" mi?
- [x] Mekânsal ses modu okunabiliyor mu? → EVET, Feature 0x72 (read_state.py)
- [x] Ses seviyesi 0x07 yanıtında mı? → HAYIR, ses scroll'u USB trafiği üretmiyor (06_scroll)
- [x] 0x07 sorgusu ne işe yarıyor? → RACE cevap kanalı (07_acilis_mekansal)
- [x] Pil yüzdesi nereden okunuyor? → Feature 0x49 / Input 0x08 (tek ölçüm, 07_acilis_mekansal)
- [ ] Pil 5'er mi bildiriliyor? Pil değişince 0x08 olayı geliyor mu?
- [x] Açılışta ANC ve Game/Chat durumu? → ANC: Feature 0x45, Game/Chat: Feature 0x62 (read_state.py)
- [x] Mikrofon durumu açılışta okunabiliyor mu? → EVET, Feature 0x67 (read_state.py)
- [x] 0x06 olayında hangi değer "sessiz"? → 00 sessiz, 01 açık; tuş ve kol aynı (listen.py)
- [ ] 0x03 / 0x04 / 0x09 ne zaman geliyor? (kulaklık aç/kapa, şarj tak/çıkar)
- [ ] 0x07 (olay), 0x5C, 0x75, 0x68, 0x51 ne anlama geliyor?
- [ ] 0x47 ve diğer 1 B Feature'lar: sidetone, DRC, mikrofon kazancı adayları
