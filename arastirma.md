# Araştırma – açık sorular

Her madde şu sırayla yazılıyor: soru · neden önemli · yöntem · risk · durum · sonuç.
Durum etiketleri: ✅ cevaplandı · 🔶 kısmen / hipotez · ⏳ bekliyor · 💤 ertelendi.

**Kural:** Firmware ya da kulaklığı bozma potansiyeli olan hiçbir şey araştırılmaz (bkz. bölüm D).

---

## A. Cihaz ölçümleri
Sadece okuma yapılır. Ölçüm araçlarını kullanıcı Rust'ta yazar (yol-haritasi.md, 4. adım).

### A1. Pil olayı ve adım büyüklüğü ✅
- **Soru:** Pil düşünce 0x08 olayı kendiliğinden geliyor mu? Değer 5'er mi değişiyor?
- **Yöntem:** Python `battery_watch.py` ile 2 dakikada bir Feature 0x49 okundu, olaylar dinlendi. Sonuç: `kayitlar/battery_log.csv` (2026-11-18, 18:26–19:59).
- **Sonuç:**
  - Pil 91 dakika boyunca %75 okundu.
  - 19:57:58'de `08 46` (%70) **kendiliğinden** geldi: önceki okumadan 61 sn sonra, sonrakinden 58 sn önce.
  - Değer ara değerlere uğramadan 75'ten 70'e düştü, yani **5'er adım**.
  - 47 okumanın 47'sinde okuma ~1 sn içinde 0x08 olayını tetikledi.
- **Tasarım kararı:** Açılışta Feature 0x49 bir kez okunur, sonra sadece olay dinlenir. Yoklama gerekmez.

### A2. Kulaklık kapalıyken ne oluyor? ⏳
- **Soru:** Dongle takılıyken kulaklık kapatılınca Feature okumaları ne döndürüyor: hata mı, son değer mi, 00 mı? Açıp kapatınca 0x03 / 0x09 olayı geliyor mu?
- **Neden önemli:** Bunu bilmezsek uygulama kulaklık kapalıyken "%0 pil, ANC kapalı" gibi yanlış bir durum gösterebilir. Bağlantı durumu ilk sürüm kapsamında (6. madde).
- **Yöntem:** Olay dinleyici açıkken kulaklığı kapat, kapalıyken durumu bir kez oku, sonra aç. Her adım arasında 10 sn bekle. Şarj kablosu gerekmiyor.
- **Risk:** Yok. Sadece izinli Feature'lar okunuyor.

### A3. Şarj durumu 💤
- Kullanıcının kararıyla ertelendi. Yöntemi: şarj kablosunu tak/çıkar, 0x03 / 0x09 olaylarını izle.

### A4. 0x04 FF = merkezleme bitti mi? 💤
- Düşük öncelik. Yeniden merkezleme (0x5E) kapsam dışı.

---

## B. Mevcut kayıtların analizi
tshark ile yapılır, cihaza dokunulmaz.

### B5. Kafa takibi akışını (0x05) ne başlatıyor? 🔶
- **Neden önemli:** Sadece C12 (Linux'ta mekânsal ses) için önemli. İlk sürümü etkilemiyor.
- **Bulgular (2026-11-18):**

| Kayıt | Olay | Akış başladı mı? |
|---|---|---|
| 07 (hizmet açık) | 36,290 sn: kulaklık tuşu → `72 02 FF` | ✅ 95 ms sonra. Arada hizmetten **hiç komut yok**, sadece her saniye gelen `23 00` |
| 08 (hizmet açık) | 18,589 sn: Output `72 02 01` | ✅ 147 ms sonra |
| 09 (hizmet kapalı) | 94,915 sn: Output `72 02 01` | ❌ 1,5 sn boyunca gelmedi |

- **Çıkarım:** Akışı başlatan özel bir komut yok. Kulaklık, mod 02 olunca akışı kendisi başlatıyor, ama bir koşul arıyor.
  - Akışın geldiği 07, 08 ve 10 kayıtlarında iki şey ortak:
    1. Game ses çıkışı (EP 0x01) açık.
    2. `23 00` kalp atışı gidiyor.
  - 09'da ikisi de yok.
- 🔶 **Hipotez:** Ya (a) Game ses akışının açık olması ya da (b) `23 00` kalp atışı gerekiyor.
- **Güvenli test (a):**
  1. Hizmeti durdur.
  2. Game çıkışında ses çal.
  3. Output 0x72 ile mod 02'yi seç (izinli komut).
  4. 0x05 akışının gelip gelmediğine bak.
- **Test (b):** Output 0x23'e yazmak gerekir. Bu rapor izin listesinde **değil**: değerini (00) resmi uygulamadan biliyoruz ama ne işe yaradığını bilmiyoruz. Ancak (a) başarısız olursa ve kullanıcı karar verirse ele alınır.

### B6. Anlamı bilinmeyen Feature'lar ⏳
- Feature okumaları sadece 07'de (hizmet açılışında) var. Diğer kayıtlarda hiç Feature okuması yok, bu yüzden değerlerin değişip değişmediği mevcut kayıtlardan görülemiyor.
- 07'deki değerler: 0x47=00, 0x4A=00, 0x5C=00, 0x68=01, 0x75=06, 0x51=`00 08 00 00 05 00 00 06 00 00 08 00`.
- Hizmetin açılışta yazdığı 0x4C/0x4D/0x4B değerleri, ham hâliyle (🔶 mikrofon ekolayzırı ön ayarları olabilir):
  ```
  4C 00 64 04   4D 00 00 00 00 BF 02 00   4D 00 01 00 B3 FF 02 04   4D 00 02 00 00 BF 02 06   4D 00 03 00 00 BF 01 08
  4C 01 64 04   4D 01 00 00 00 00 02 00   4D 01 01 00 4D BF 02 02   4D 01 02 00 00 BF 04 03   4D 01 03 00 00 BF 05 06
  4C 02 64 03   4D 02 00 00 00 00 00 00   4D 02 01 00 00 FF 00 01   4D 02 02 00 4C FF 02 04
  4B 00
  ```
- **Sonraki adım (sonraki sürüm için):** Hizmet açıkken yeni bir kayıt (`11_uygulama_ayarlari`) alınır. Uygulamada sırayla değiştirilir, aralarında 10'ar sn beklenir ve saatler not edilir:
  - sidetone aç/kapa ve seviye
  - DRC
  - mikrofon kazancı
  - mikrofon ekolayzırı (Natural / Bright / Powerful)
- **Risk:** Yok. Yazmayı resmi uygulama yapıyor, biz sadece gözlemliyoruz.

---

## C. Linux / platform

### C7. hidraw ile Windows hidapi arasındaki farklar 🔶
- **Bilinen:**
  - Linux hidraw'da Feature okumasında cevabın ilk baytı Report ID oluyor. Tampon, rapor uzunluğu + 1 bayt olmalı.
  - hidapi bu kuralı iki platformda da aynı API ile sunuyor.
  - Windows'ta hidapi cevabı 64 bayta tamamlıyordu.
- **Kod kuralı:** Uzunluklar her zaman descriptor'daki rapor uzunluklarına göre kırpılmalı. Gelen uzunluğa güvenilmez. Böylece kod iki platformda da aynı çalışır.
- **Doğrulama:** WSL2'de (C10) Feature okuma ve olay okuma uzunlukları ölçülür.

### C8. udev kuralı ve dağıtım şekli 🔶
- **Bilinen:**
  - Kural `hidraw` alt sistemine VID/PID ile eşleşmeli. USB seviyesindeki eşleşme hidraw düğümüne izin vermiyor.
  - İzin için `TAG+="uaccess"` kullanılmalı (oturumdaki kullanıcıya erişim verir). `MODE="0666"` fazla geniş izin verdiği için önerilmiyor.
  - Dosya adındaki numara `73-seat-late.rules`'tan küçük olmalı, örneğin `70-…`.
  - Paketler kuralı `/usr/lib/udev/rules.d/` altına kurar. `/etc/udev/rules.d/` altındaki aynı adlı dosya onu geçersiz kılar.
  - Kontrol: `udevadm info /dev/hidrawN` çıktısında `uaccess` etiketi görünmeli.
- **Dağıtım şekline etkisi:**
  - .deb, .rpm ve AUR paketleri kuralı kendisi kurabilir.
  - Flatpak ve AppImage kuramaz, kullanıcının kuralı elle kurması gerekir.
  - Örnek emsal: Debian'ın hidapi paketi kendi kuralını kuruyor.
- Kuralı kullanıcı 8. adımda yazacak.

### C9. Linux'ta ses (Game / Chat / mikrofon) ⏳
- **Beklenen:** Ses arayüzleri standart USB Audio Class. `snd-usb-audio` sürücüsüyle iki çıkış (Game, Chat) ve bir mikrofon girişi görünmeli.
- **Risk notu:** Başka bir modelde (Quantum 200) Linux'ta mikrofonun görünmediği raporlanmış.
- **Doğrulama:** Bu ancak gerçek bir Linux'ta (canlı USB) yapılabilir. WSL'de ses bu şekilde test edilemez.

### C10. Linux kurmadan test: WSL2 + usbipd-win 🔶 (büyük olasılıkla mümkün)
- ✅ Bu bilgisayardaki WSL çekirdeğinde (6.18.33.2) gerekli seçenekler açık:
  - `CONFIG_HIDRAW=y`
  - `CONFIG_USB_HID=m`
  - `CONFIG_USBIP_CORE=m` / `CONFIG_USBIP_VHCI_HCD=m`
  - `CONFIG_SND_USB_AUDIO=m`
- **Eksikler:**
  - Gerçek bir dağıtım kurulu değil, sadece `docker-desktop` var. Örneğin Ubuntu kurulmalı.
  - usbipd-win kurulu değil.
- **Dikkat:** Dongle WSL'e bağlıyken Windows onu kullanamaz, yani ses kesilir.
- **Sırası:** Yol haritasında 8. adım. Rust kodu hazır olunca yapılır.

### C11. HeadsetControl'de JBL desteği var mı? ✅ Yok
- Cihaz listesinde JBL/Harman yok. Desteklenen markalar: Logitech, Corsair, SteelSeries, HyperX, Sony, Razer ve birkaç başkası.
- Proje artık C++20 ile yazılıyor. ANC özelliğini de destekliyor (Sony INZONE H9 II), yani 910P'nin özellikleri projenin yapısına uyar.
- **İleride bir seçenek:** Kendi uygulamamız bitince bulunan protokol HeadsetControl'e katkı olarak da gönderilebilir.

### C12. Linux'ta mekânsal ses 🔶 (uzun vadeli)
- PipeWire'ın filter-chain modülünde SOFA tabanlı bir **spatializer** var.
  - Kontrolleri: `Azimuth` (0–360°), `Elevation` (−90…90°), `Radius`.
  - Bu kontroller çalışırken değiştirilebiliyor.
- **Teorik fikir:** 0x05 quaternion'undan yaw açısı hesaplanır ve Azimuth'a beslenir. Bu, Linux'ta kafa takipli mekânsal ses demek. Önce B5 çözülmeli.
- Kontrolün çalışırken nasıl değiştirileceği (`pw-cli set-param` gibi) henüz doğrulanmadı.

### C13. Rust kütüphaneleri ✅ (2026-11-18)
- `hidapi` 2.6.7 (2026-08-27). Linux'ta varsayılan özellik `linux-static-hidraw`, yani hidraw arka ucu kullanılıyor, libusb gerekmiyor. Windows'ta ek ayar gerekmiyor.
- `ksni` 0.3.7 (2026-10-20). StatusNotifierItem tepsi simgesi sağlıyor. KDE'de doğrudan çalışıyor, GNOME'da AppIndicator eklentisi gerekiyor.
- CLI için `clap`. GUI kararı (gtk4-rs / iced / slint) CLI bitince verilecek.

---

## D. Kapsam dışı (ASLA)
- RACE kanalı (Output 0x06): komut gönderme, anahtar okuma, deneme.
- Feature 0xF0–0xFB, COL02 0x9A: okuma ve yazma.
- Feature 0x5E, 0x4C, 0x4D, 0x4B'ye yazma.
- Bilinmeyen raporlara deneme amaçlı değer gönderme.
- Firmware sürümü, güncellemesi ve fabrika ayarlarıyla ilgili her şey.

## Kaynaklar
- [JBL 910P destek sayfası](https://support.jbl.com/product-registration/QUANTUM910PWIRELESS.html) (ANC tuşu açıklaması bizim ölçümümüzle çelişiyor)
- [HeadsetControl README](https://raw.githubusercontent.com/Sapd/HeadsetControl/master/README.md)
- [Linux hidraw belgesi](https://kernel.org/doc/html/v5.11/hid/hidraw.html), [SDL hid_get_feature_report](https://wiki.libsdl.org/SDL2/SDL_hid_get_feature_report)
- [Debian hidapi udev kuralı](https://sources.debian.org/src/hidapi/0.15.0-2/udev/69-hid.rules), [Toradex: hidraw kuralı ve 73-seat-late](https://community.toradex.com/t/usb-device-udev-rule-is-not-triggered/29977/4), [AUR: uaccess ve 0666 karşılaştırması](https://aur.archlinux.org/cgit/aur.git/tree/83-hhd-user.rules?h=hhd-user)
- [Microsoft: USB cihazlarını WSL'e bağlama](https://devblogs.microsoft.com/commandline/?p=7083), [usbipd-win](https://github.com/dorssel/usbipd-win), [WSL hidraw issue](https://github.meowingcats01.workers.dev/microsoft/WSL/issues/10581)
- [PipeWire filter-chain belgesi](https://docs.pipewire.org/page_module_filter_chain.html), [Topluluk: PipeWire ile sanal surround](https://lemmy.nekusoul.de/post/3937)
- [Garuda forumu: JBL Quantum 200 mikrofon sorunu](https://forum.garudalinux.org/t/jbl-headset-microphone-isnt-detected/17175.md)
- crates.io: [hidapi](https://crates.io/crates/hidapi), [ksni](https://crates.io/crates/ksni)
