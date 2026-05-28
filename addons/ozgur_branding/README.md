# Özgür Rubber Branding

Custom Odoo 19 addon that applies Özgür Rubber's corporate visual identity
to backend, frontend, and login surfaces.

## What it does
- Overrides Bootstrap and Odoo SCSS variables (token-first)
- Loads self-hosted Inter and JetBrains Mono fonts
- Applies company logo and favicon via post-install hook
- Adds light component refinements (monospace numeric fields, section spacing)

## What it does NOT do (Faz 1 scope)
- Does NOT override `web.login_layout` or `web.frontend_layout` templates
- Does NOT touch OWL components
- Does NOT add dark mode
- Does NOT customize per-module views

## Install
```
docker compose restart odoo
# In Odoo: Apps → Update Apps List → search "Özgür" → Install
```

## TODO

- **PDF→SVG dönüşümü yapılamadı.** `pdf2svg`, `inkscape` ve `magick` (ImageMagick) host'ta da Odoo container'da da bulunamadı; lokalde Python da yok (Windows Store stub). `_brand_assets/BEYAZ.pdf` ve `_brand_assets/OZGUR RUBBER LOGO.pdf` `static/img/` altına `BEYAZ.pdf` ve `OZGUR_RUBBER_LOGO.pdf` olarak kopyalandı ama **`logo.svg` ve `logo_dark.svg` üretilmedi**. Bir çözüm yöntemi seç:
  - `pdf2svg` veya Inkscape kur ve manuel çalıştır:
    `pdf2svg addons/ozgur_branding/static/img/BEYAZ.pdf addons/ozgur_branding/static/img/logo.svg`
  - veya tasarım aracında PDF'leri açıp SVG export et ve dosyayı `static/img/logo.svg` + `static/img/logo_dark.svg` olarak koy.
- **`logo_dark.png` yok.** `hooks.py` logo aramasında sırasıyla `logo.svg → logo_icon.png → logo_dark.png` deniyor; şu an sadece `logo_icon.png` (emblem) mevcut, post-init hook'u onu `res.company.logo`'ya yazacak. Tam logo (BEYAZ.pdf vektör hali) kullanılamadığı için emblem ile başlayacak. Light/dark logo ayrımı isteniyorsa `logo_dark.png`/`.svg` eklenmeli.
- **`views/webclient_templates.xml` Faz 1'de boş bırakıldı** — brief §4.8 talimatı bu (login arka planı, app launcher kart stili Faz 2 işi).
- **`logo_icon.png` raster (1.9MB orijinal).** `res.company.logo`'ya base64 olarak yazılınca büyük olacak; vektör tercih edilir (PDF→SVG TODO'su çözülünce).

## Bilinçli sapmalar

**1. `__init__.py`'de `_post_init_apply_branding` re-export ediliyor** (brief §4.1'den minimal sapma).
   - Brief'teki tek satır: `from . import hooks`
   - Uygulanan: ek olarak `from .hooks import _post_init_apply_branding`
   - **Gerekçe:** Odoo 19'un `odoo/modules/loading.py:243` satırı post_init_hook'u
     `getattr(py_module, post_init)(env)` ile çağırıyor; burada `py_module` modülün
     `__init__.py`'siyle yüklenmiş package objesi. Sadece `from . import hooks`
     yapıldığında `_post_init_apply_branding` package seviyesinde değil
     `package.hooks` altında oluyor → `AttributeError`. Re-export bunu giderir.
     Doğrulandı: install hatası `AttributeError: module 'odoo.addons.ozgur_branding'
     has no attribute '_post_init_apply_branding'`.
   - **Etkisi:** Doctrine ihlali yok (brief'in kod örneğinden minimal pratik düzeltme,
     gerçek davranış brief'in niyetiyle aynı).

**2. Manifest `category` 'Theme' → 'Customization'** (brief §4.2'den sapma).
   - **Gerekçe:** Odoo `website` modülü `addons/website/models/ir_module_module.py`
     `get_themes_domain()` ile `category_id = base.module_category_theme` olan
     modülleri "theme" sayıyor. `website._get_active_addons_list(website_id=1)`
     bu theme'lerden aktif olmayanları frontend bundle listesinden DÜŞÜRÜYOR.
     Brief'in `'category': 'Theme'` değeri tam olarak bu filtreye yakalıyor →
     `/web/login` + portal + website-public sayfalarda SCSS asset'lerimiz
     bundle'a girmiyor, branding görünmüyor.
   - Doğrulama: `_get_active_addons_list(website_id=1)` çağrısı `'Theme'`
     kategorisinde iken 194 modül (ozgur düşmüş), `'Customization'`'a
     değiştirince 195 (ozgur dahil).
   - **Uygulanan:** `category` = `'Customization'`.
   - **Etkisi:** Brief'in "login yüzeylerini etkiler" hedefiyle uyumlu;
     theme aktivasyon UI'ı (Website Settings → Theme picker) bu modülü
     "theme" olarak göstermez (zaten gerçek bir theme değil — global SCSS
     override modülü).

**3. Manifest'e `website.assets_frontend` bundle eklendi** (brief §4.2'den ek).
   - **Gerekçe:** Sigorta. Yukarıdaki #2'deki category fix asıl çözüm; bu ek
     bundle declaration `website` modülü kurulu olduğu senaryolarda asset'in
     website renderi'na ayrıca dahil olmasını garanti ediyor.
   - **Uygulanan:** Aynı 3 SCSS dosyasını `website.assets_frontend` bundle'ına
     da ekledik (prepend variables + fonts + branding).
   - **Etkisi:** `website` modülü yoksa bu bundle no-op olur; zarar yok.

Doctrine'in 10 maddesinin tümüne uyuldu:
- Odoo core'a dokunulmadı (sadece `addons/ozgur_branding/` altına yazıldı)
- Repo root dosyaları (`docker-compose.yml`, `config/odoo.conf`, repo `README.md`) değiştirilmedi
- `position="replace"` kullanılmadı (XML view inheritance yok zaten Faz 1'de)
- ORM bypass / `self.env.cr.execute` yok
- Super atlama yok (override yok)
- Gereksiz `sudo()` yok
- OWL dışı frontend framework eklenmedi
- Hardcoded credentials yok
- Mevcut Odoo davranışı kırılmıyor (sadece görsel override)
- Belirsizlik = TODO (yukarıdaki TODO bölümüne yazıldı)

Brief §4.5'in `_variables.scss` "DİKKAT" uyarısı: 19 adet `$o-*` değişkeninin tümü Odoo 19 web modülünde mevcut olduğu Docker container içinde `grep` ile doğrulandı — hiçbiri çıkarılmadı.
