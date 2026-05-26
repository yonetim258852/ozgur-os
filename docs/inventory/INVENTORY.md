# Odoo Custom Addons Inventory
_Tarama tarihi: 2026-05-26T04:39:17Z_
_Tarama yapan: Claude Code_
_Repo commit: 76ffa43d0a2c03a432a5a3bde2ef7d0c41f01424_
_Tarama kapsamı: repo kökünden recursive `__manifest__.py` araması (`.git/` hariç)_

## 1. Özet
- Toplam custom modül sayısı: **0**
- Inheritance ağırlığı (toplam xpath): 0
- Component patch sayısı: 0
- RED FLAG bulgu sayısı: 0

> Bu repo henüz **hiçbir custom Odoo addon içermiyor**. `docker-compose.yml`
> içinde `./addons:/mnt/extra-addons` mount tanımı bulunmasına rağmen, repo
> kökünde `addons/` dizini fiziksel olarak **yok** ve repo genelinde tek bir
> `__manifest__.py` dosyası dahi bulunamadı. Aşağıdaki bölümlerin tamamı bu
> nedenle boş / N/A olarak raporlanmıştır.

### Repo içeriği (referans)
```
./README.md
./docker-compose.yml
./config/odoo.conf
```
(Yukarıdaki liste `.git/` hariç tüm dosyaları kapsamaktadır.)

## 2. Modül Listesi

| modül_adı | sürüm | depends | category | license | author | summary |
|-----------|-------|---------|----------|---------|--------|---------|
| _(modül yok)_ | — | — | — | — | — | — |

## 3. Custom Yük Haritası

Hiç modül bulunmadığı için yük haritası boştur.

- XML view inheritance
    - `inherit_id="..."` sayısı: 0
    - `<xpath>` sayısı: 0
    - `position="replace"` sayısı: 0
- Python model inheritance
    - `_inherit = "..."` sayısı: 0
    - `_inherits = {...}` (delegation) sayısı: 0
    - `_name = "..."` (yeni model) sayısı: 0
- JS/OWL component patches
    - `from "@web/core/utils/patch"` import sayısı: 0
    - `patch(...)` çağrı sayısı: 0
- Asset bundle ekleri
    - `__manifest__.py > assets` giriş sayısı: 0
    - `web.assets_backend` / `web.assets_frontend` / `point_of_sale.assets` dağılımı: 0 / 0 / 0
- Security
    - `ir.model.access.csv` toplam satır sayısı: 0
    - `security/*.xml` (record rule) dosya sayısı: 0

## 4. RED FLAG Bulguları

| dosya | satır | pattern | bağlam |
|-------|-------|---------|--------|
| _(bulgu yok — taranacak modül kodu yok)_ | — | — | — |

Tarama yapılacak Python/XML/JS dosyası bulunmadığı için aşağıdaki pattern'lerin
tamamı **0 bulgu** ile sonuçlandı:
- `self.env.cr.execute`
- `.sudo()`
- `position="replace"`
- `@api.model_create_multi` olmayan `create` override
- `super()` çağrısı içermeyen `def write` / `def create` / `def unlink` override
- Odoo dışı frontend framework imports: `react`, `vue`, `angular`, `alpine`
- Hardcoded credentials (`password=`, `api_key=`, `token=` literal)

> Not: `config/odoo.conf` ve `docker-compose.yml` içinde DB parolası
> (`odoo2026`) düz metin olarak yer almaktadır. Bu **addon kodu** kapsamı
> dışındadır, dolayısıyla RED FLAG tablosuna alınmamıştır; ancak operasyonel
> güvenlik açısından ayrı bir review konusu olabilir.

## 5. Uyumluluk Sinyalleri

- Manifest `version` alanı dağılımı:
    - `17.0.*`: 0
    - `18.0.*`: 0
    - `19.0.*`: 0
    - diğer / yok: 0
- Eksik manifest alanları (license / version / summary): N/A (manifest yok)

Hedef platform sürümü (manifest'lerden değil) `docker-compose.yml` üzerinden
**Odoo 19** olarak görünmektedir (`image: odoo:19`). Bu bilgi bir manifest
taramasından gelmediği için aşağıdaki "Belirsizler" bölümüne de düşüldü.

## 6. Belirsizler

- **BELİRSİZ:** Repo'da `addons/` dizini fiziksel olarak mevcut değil, fakat
  `docker-compose.yml` bunu konteynerin `/mnt/extra-addons` yoluna mount
  ediyor. Custom modüllerin başka bir kaynaktan (submodule, CI, ayrı klon,
  henüz yazılmamış) bekleniyor olup olmadığı bu statik taramadan
  anlaşılamamaktadır.
- **BELİRSİZ:** Hedeflenen Odoo sürümünün gerçekten 19.0 olup olmadığı
  yalnızca Docker image etiketinden çıkarılabildi; modül manifest'lerinden
  doğrulanamadı (manifest yok).
- **BELİRSİZ:** README'de "addons/ - Custom modullerimiz" denmesine rağmen
  dizinin henüz oluşturulmamış olması — niyet bildirimi mi yoksa eksik commit
  mi olduğu bu taramadan tespit edilemez.
