# Backlink Manager Pro

Türkçe arayüzlü, masaüstü tabanlı bir backlink ve içerik yönetim aracı. Site listesini yönetir,
spintax şablonlarından makale üretir, görsel ekler ve WordPress REST API üzerinden toplu yayın yapar.
Yedekleme/geri yükleme ve yerel yardım ekranı içerir.

> **Bu sürüm açık kaynaqtır.** Lisans doğrulama kodu kaldırılmıştır; uygulama çevrimdışı ve ücretsiz çalışır.
> WebAdHere markası ve destek bağlantıları korunmuştur.

---

## Özellikler

- Site yönetimi: hedef WordPress sitelerini ekleme/düzenleme, API türü seçimi
- Bağlantı yönetimi: backlink domain listesi ve kategori eşleştirmesi
- İçerik üretimi: spintax destekli başlık/makale şablonları, otomatik görsel seçimi
- Toplu yayın: WP REST API (`/auth`, `/posts`, `/upload-image`) üzerinden paralel gönderim
- Yedekleme / geri yükleme: tüm veri dosyalarını tek arşive alma
- Türkçe arayüz, koyu tema (CustomTkinter)

## Kurulum

```powershell
python -m pip install -r requirements.txt
python main.py
```

Exe dosyasını kullanacaksan sürüm sayfasındaki `Backlink Manager Pro.exe` dosyasını indirip
çalıştırabilirsin (Windows, imzasız exe → "More info" → "Run anyway").

## Yapılandırma

Uygulama aynı klasörde üç JSON dosyası kullanır. Repoda **boş şablonlar** gelir:

| Dosya | İçerik |
|---|---|
| `sites.json` | Hedef siteler: `url`, `username`, `auth_token`, `api_type` |
| `backlinks.json` | Backlink domain listesi |
| `articles.json` | Makale şablonları: `title`, `content`, `image_urls` |

> **Güvenlik:** `sites.json` içindeki `auth_token` değerleri oturum anahtarıdır.
> Kendi verilerini girdikten sonra bu dosyaları **asla** commit etme veya paylaşma.

## WordPress API eklentisi

`backlink-manager-api.php` (veya hazır `backlink-manager-api.zip`) hedef WordPress sitesine
kurulacak eklentidir. JWT anahtarını `wp_salt('auth')` ile kendisi üretir; şu uçları açar:

- `POST /wp-json/backlink-manager/v1/auth`
- `POST /wp-json/backlink-manager/v1/posts`
- `POST /wp-json/backlink-manager/v1/upload-image`

## Lisans

GPL-3.0 — detaylar için [LICENSE](LICENSE).

Destek ve marka: [WebAdHere](https://webadhere.com) · info@webadhere.com

---

## English summary

Desktop tool for managing backlinks and publishing spintax-generated articles to WordPress sites
through the REST API. This is the open-source build: license validation has been removed, all data
files ship empty, and no credentials are included. GPL-3.0.
