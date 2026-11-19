# CLAUDE.md – Çalışma anlaşması

JBL Quantum 910P için Linux kontrol uygulaması. Durum ve sıradaki adım: [README.md](README.md).

## Kullanıcının talimatları (kalıcı)
- **Kodun tamamını kullanıcı yazar.** Ürün kodu da ölçüm/araştırma araçları da buna dahil.
  - Claude proje dosyalarına kod yazmaz. Görevi yol göstermek: adımı tarif eder, kavramı açıklar, yazılan kodu inceler, hata ayıklamaya yardım eder.
  - Kod örneği verilecekse kısa olmalı ve sohbette kalmalı. Dosyaya yazılmaz.
- **Dil: Rust.** Kullanıcı C# biliyor ve Python deneyimi var. Rust kavramları anlatılırken C# karşılığı verilir.
- **Hedef: tüm Linux dağıtımları.** Geliştirme şimdilik Windows'ta yapılıyor, Linux sistemi henüz yok.
- **Talimatlar md dosyalarına işlenir.** Kullanıcının yeni bir talimatı bu dosyaya eklenir. Bulgular `protocol.md` / `arastirma.md` dosyalarına, plan değişiklikleri `yol-haritasi.md` dosyasına yazılır.
- **Büyük değişiklik ve arşivleme kullanıcı "başla" deyince yapılır.** Önce plan sunulur.
- **Cevaplar Türkçe olur.**

## ⚠️ Güvenlik (ayrıntı: [protocol.md](protocol.md))
- Yazılabilecek raporlar sadece **Feature 0x46** (ANC) ve **Output 0x72** (mekânsal ses).
- **ASLA** dokunulmayacaklar:
  - Output 0x06 (Airoha RACE kanalı)
  - Feature 0xF0–0xFB
  - COL02 0x9A
- Okuma da yalnızca resmi uygulamanın okuduğu Feature'larla sınırlı.
- Firmware güncellemesine ya da kulaklığı bozabilecek işlemlere dair araştırma ve kod **yapılmaz**.
- Yeni bir rapor ancak resmi uygulamanın onu nasıl kullandığı kayıtla doğrulandıktan sonra kullanılabilir.

## Dosya düzeni
| Yol | İçerik |
|---|---|
| `README.md` | Özet, durum, sıradaki adım |
| `protocol.md` | Çözülmüş protokol (ana kaynak) |
| `features.md` | Kulaklık özellikleri, sürüm kapsamı |
| `device-info.md` | USB/HID yapısı |
| `arastirma.md` | Açık sorular, yöntem, risk, sonuç |
| `yol-haritasi.md` | Rust öğrenme + geliştirme adımları |
| `kayitlar/` | Wireshark kayıtları (pcapng), ölçüm logları |
| `descriptors/` | UsbTreeView çıktısı |
| `eski-md-dosyalari/` | Arşiv: önceki md sürümleri (değiştirilmez) |
| `eski-python/` | Arşiv: Python deneme kodu. Referans için tutuluyor. `.venv` ile çalışır. |

## Arşiv düzeni
md dosyaları baştan yazılacaksa eski hâlleri önce `eski-md-dosyalari/` klasörüne taşınır. İkinci bir arşivleme olursa tarihli alt klasör kullanılır (`eski-md-dosyalari/2026-11-18/`).

## Araçlar
- Wireshark/tshark kurulu: `C:\Program Files\Wireshark\tshark.exe`. Kayıt analizi cihaza dokunmaz.
- WSL2 kurulu, çekirdek 6.18. usbipd-win kurulu değil.
- Rust henüz kurulu değil (yol haritasında 0. adım).
