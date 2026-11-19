# Yol haritası – Rust

Kodu kullanıcı yazar, Claude yol gösterir (bkz. CLAUDE.md). Her adım küçük ve çalışan bir program üretir.
Her adımda şunlar var:
- **Kavram:** Bu adımda öğrenilecek Rust konusu. Varsa C# karşılığı da verilir.
- **Çıktı:** Adım sonunda elde olacak program.
- **Bitti sayılır:** Adımın tamamlandığını gösteren kontrol.

Python deneme kodu (`eski-python/`) bir **referans**. Mantığı oradan okunabilir ama kopyalanmaz, Rust'ta yeniden düşünülür.

| # | Adım | Durum |
|---|---|---|
| 0 | Kurulum | ⏳ sıradaki |
| 1 | Cihazları listele | ⏳ |
| 2 | Durumu oku | ⏳ |
| 3 | Olay dinleyici | ⏳ |
| 4 | Ölçüm araçları | ⏳ |
| 5 | Çekirdek kütüphane | ⏳ |
| 6 | Yazma (ANC, mekânsal ses) | ⏳ |
| 7 | CLI | ⏳ |
| 8 | Linux'ta test (WSL2) | ⏳ |
| 9 | GUI / tepsi simgesi | ⏳ |
| 10 | Paketleme | ⏳ |

---

### 0. Kurulum
- **Yapılacaklar:**
  - `rustup` ile Rust kur. Windows'ta "MSVC" araç zinciri gerekiyor, kurulum sihirbazı Visual Studio Build Tools'u önerecek.
  - VS Code'a `rust-analyzer` eklentisini kur.
  - `cargo new` ile bir proje oluştur.
- **Kavram:**
  - `cargo` ≈ `dotnet` CLI.
  - `Cargo.toml` ≈ `.csproj`.
  - crates.io ≈ NuGet.
- **Bitti sayılır:** `cargo run` "Hello, world!" yazdırıyor.
- **Karar verilecek:** Rust projesi bu klasörde nereye konacak? Öneri: kökte tek bir `Cargo.toml`. Sonra kütüphane, CLI ve araçlar için bir workspace yapısına geçilir.

### 1. Cihazları listele
- **Yapılacaklar:** `hidapi` crate'ini ekle. VID 0x0ECB / PID 0x20A2'nin HID koleksiyonlarını listele: usage page, interface, yol.
- **Kavram:**
  - Bağımlılık eklemek.
  - `Result<T, E>`, C#'taki exception yerine dönüş değeriyle hata yönetimi.
  - `?` operatörü.
  - `for` ile iterator kullanmak.
- **Çıktı:** `eski-python/tools/list_devices.py` programının Rust karşılığı.
- **Bitti sayılır:** Çıktıda 0xFF13 koleksiyonu görünüyor.

### 2. Durumu oku
- **Yapılacaklar:** 0xFF13 koleksiyonunu aç. Beş Feature'ı oku (0x45, 0x49, 0x62, 0x67, 0x72) ve anlamlarıyla yazdır.
- **Kavram:**
  - `enum` ve `match`: C#'taki switch ifadesine benzer ama derleyici eksik kalan dalları yakalar.
  - `TryFrom<u8>`: bilinmeyen değeri çökmeden ele almak.
  - Slice'lar (`&[u8]`).
- **Bitti sayılır:** Kulaklıkta görünen durum ekrana doğru yazılıyor.
- **Dikkat:**
  - Okuma izin listesi uygulanmalı. Sadece bu beş Feature okunur.
  - Uzunluklar descriptor'a göre kırpılmalı (arastirma.md C7).

### 3. Olay dinleyici
- **Yapılacaklar:** Interrupt okuma döngüsü kur. Olayları çözümle, 0x05 akışını gizle.
- **Kavram:**
  - `loop`.
  - `Option<T>`: C#'taki nullable'a benzer.
  - Zaman aşımlı okuma.
  - Ctrl+C ile temiz çıkış.
- **Çıktı:** `eski-python/tools/listen.py` programının Rust karşılığı.

### 4. Ölçüm araçları → araştırma A2
- **Yapılacaklar:** Kulaklık aç/kapa denemesi için olay dinleyici + kapalıyken durum okuma. Çıktı bir CSV log dosyasına yazılır.
- **Kavram:**
  - Dosyaya yazmak.
  - Zaman bilgisi.
  - Hataları ayırt etmek: "cihaz yok" ile "cevap beklenmeyen" farklı durumlar.
- **Bitti sayılır:** arastirma.md A2 cevaplandı.

### 5. Çekirdek kütüphane
- **Yapılacaklar:** 1–4. adımlardaki kodu bir `lib` crate'inde topla:
  - protokol tanımları
  - durum okuma
  - olay ayrıştırma
  - izin listesi
- **Kavram:**
  - Modüller ve görünürlük (`pub`).
  - Birim testleri (`#[cfg(test)]`).
  - **newtype ile güvenlik:** Yazılabilir raporları ayrı bir tip yap. Böylece yasaklı bir rapora yazan kod derlenmez bile.
- **Bitti sayılır:** `cargo test` geçiyor. Yasaklı raporları (0x06 Output, 0xF0–0xFB, 0x9A) reddeden testler var.

### 6. Yazma: ANC ve mekânsal ses
- **Yapılacaklar:**
  - `set_anc`: Feature 0x46 gönderilir, ardından 0x02 olayı ya da Feature 0x45 ile onay beklenir.
  - `set_spatial`: Output `[72, yeni, mevcut]` gönderilir, ardından Feature 0x72 okunarak onaylanır.
- **Kavram:**
  - Kendi hata tipini tanımlamak.
  - Zaman aşımı.
  - Onay beklerken gelen diğer olayları kaybetmemek (kuyruk).
- **Karar verilecek:** Onay stratejisi. Olay gelmezse ne olacak? Kullanıcı tam o anda tuşa basarsa ne olacak?

### 7. CLI
- **Yapılacaklar:** `clap` ile şu komutlar:
  - `durum`
  - `dinle`
  - `anc <kapali|anc|talkthru>`
  - `mekansal <kapali|sabit|kafa>`
- **Kavram:** derive makroları (C#'taki attribute'lara benzer), alt komutlar.

### 8. Linux'ta test (WSL2) → araştırma C7, C8, C10
- **Yapılacaklar:**
  - WSL'e bir Ubuntu dağıtımı kur.
  - usbipd-win kur ve dongle'ı WSL'e bağla.
  - udev kuralını yaz.
  - CLI'ı Linux'ta derle ve çalıştır.
- **Bitti sayılır:** `durum` ve `anc` komutları Linux'ta çalışıyor.
- **Not:** Sesi (C9) WSL'de test etmek mümkün değil. Bunun için ileride canlı USB gerekir.

### 9. GUI / tepsi simgesi
- **Yapılacaklar:** Pil göstergesi ve ANC ile mekânsal ses seçimi.
- **Karar verilecek:**
  - Tepsi simgesi için `ksni` mi kullanılacak?
  - Pencere için gtk4-rs mi, iced mi, slint mi?

### 10. Paketleme
- **Yapılacaklar:** .deb, .rpm ve AUR paketleri (udev kuralını kendileri kurabiliyorlar), ayrıca AppImage.
- Flatpak kısıtları için bkz. arastirma.md C8.
