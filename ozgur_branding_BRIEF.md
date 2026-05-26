# CLAUDE CODE BRIEF — `ozgur_branding` modülü (Faz 1)

> **Hedef:** Odoo 19 Community için Özgür Rubber kurumsal kimliğini uygulayan
> bir custom addon oluştur. Token-first design system + Inter/JetBrains Mono
> tipografi + Navy/Gold/Stone palette + logo + favicon. Backend + Frontend +
> Login yüzeylerini etkiler.
>
> **Çalışma dizini:** Bu brief'in çalıştırıldığı repo `yonetim258852/ozgur-os`.
> Odoo 19 Docker compose'la ayakta. Custom addons mount path: `./addons/`.

---

## 1. DOCTRINE — UYMAK ZORUNLUSUN

Bu kurallar **mutlak**. Tek bir maddeyi bile bilinçli ihlal edersen, ihlali
README.md'nin "Bilinçli sapmalar" bölümüne yaz ve gerekçesini belge altına al.

1. **Odoo core'a dokunma.** `addons/web/`, `addons/base/`, `addons/website/`
   vb. ALTINDA hiçbir dosyayı değiştirme, taşıma, silme. Sadece yeni dosyalar
   oluşturduğun konum: `addons/ozgur_branding/`.
2. **Repo root dosyalarına dokunma.** `docker-compose.yml`, `config/odoo.conf`,
   `README.md` (repo kökündeki) sabit kalacak.
3. **`position="replace"` YASAK.** View inheritance yaparken sadece
   `before/after/inside/attributes` kullan.
4. **ORM bypass yok.** `self.env.cr.execute` yok.
5. **Super atlama yok.** Method override edersen mutlaka `super().method_name()`
   çağır.
6. **Gereksiz `sudo()` yok.** Sadece security framework gerçekten gerekli
   olduğunda, gerekçesini koddaki yorumda açıkla.
7. **OWL dışı frontend framework yok.** React/Vue/Angular/Alpine ekleme.
8. **Hardcoded credentials yok.** Hiçbir şifre/key/token literal değer olarak
   koda girmesin.
9. **Mevcut çalışan davranışı kırma.** Standart Odoo'nun login/navbar/form
   davranışı kırılmamalı, sadece görsel olarak değişmeli.
10. **Belirsizlik = TODO.** Brief'te cevabı olmayan bir soru çıkarsa: tahmin
    yapma. `README.md > TODO` bölümüne yaz.

---

## 2. KULLANICI GİRİŞLERİ — Brand Assets

Repo root'unda `_brand_assets/` klasörü olacak. Kullanıcı şu dosyaları oraya
koyacak (sen yerleştirmeyeceksin, sadece okuyacaksın):

| Dosya | Açıklama | Hedef |
|-------|----------|-------|
| `BEYAZ.pdf` | Tam logo (beyaz arkaplan, vektör) | `static/img/logo.svg` (dönüştürülecek) |
| `logo_siyah_kaliteliden_düsüge.JPG` | Siyah arkaplan, beyaz/altın logo | `static/img/logo_dark.png` |
| `LOGO_ICON__1_.ico` | Favicon | `static/img/favicon.ico` (doğrudan kopya) |
| `1779773902880_image.png` | Yedek logo varyantı | gerekirse fallback |

**`_brand_assets/` dizini yoksa:** `README.md > TODO` bölümüne not düş ve
`static/img/` altında `PLACEHOLDER.txt` dosyaları bırak.

**PDF→SVG dönüşümü:** Sırayla şunları dene:
1. `pdf2svg` komutu varsa → `pdf2svg BEYAZ.pdf static/img/logo.svg`
2. Inkscape varsa → `inkscape BEYAZ.pdf --export-type=svg --export-filename=static/img/logo.svg`
3. ImageMagick fallback (raster ama 4x DPI ile): `convert -density 300 BEYAZ.pdf static/img/logo.png`

Hiçbiri yoksa README'ye TODO yaz, .pdf'i olduğu gibi kopyala.

---

## 3. DOSYA AĞACI — TAM YAPILANDIRMA

```
addons/ozgur_branding/
├── __init__.py
├── __manifest__.py
├── README.md
├── hooks.py
├── data/
│   └── res_company_data.xml
├── static/
│   ├── description/
│   │   ├── icon.png               (256x256, Apps listesi için)
│   │   └── index.html             (Apps detay sayfası)
│   ├── img/
│   │   ├── logo.svg               (full logo)
│   │   ├── logo_dark.png          (dark bg varyantı)
│   │   ├── logo_icon.png          (sadece kuş emblem, 512x512)
│   │   └── favicon.ico
│   ├── fonts/
│   │   ├── Inter-Regular.woff2
│   │   ├── Inter-Medium.woff2
│   │   ├── Inter-SemiBold.woff2
│   │   ├── JetBrainsMono-Regular.woff2
│   │   └── JetBrainsMono-Medium.woff2
│   └── src/
│       └── scss/
│           ├── _variables.scss    (PREPENDED — tokens + bootstrap + odoo override)
│           ├── _fonts.scss        (@font-face)
│           └── branding.scss      (component refinements)
└── views/
    └── webclient_templates.xml    (login + navbar template tweaks)
```

---

## 4. DOSYALARIN İÇERİĞİ

### 4.1 `__init__.py`

```python
from . import hooks
```

### 4.2 `__manifest__.py`

```python
{
    'name': 'Özgür Rubber Branding',
    'version': '19.0.1.0.0',
    'category': 'Theme',
    'summary': 'Corporate branding for Özgür Rubber: tokens, typography, palette, logo.',
    'description': """
Özgür Rubber Branding
=====================
Token-first design system applied to Odoo 19 backend + frontend + login.

Provides:
- Navy / Gold / Warm Stone color ramps as SCSS tokens
- Inter (UI) + JetBrains Mono (numeric) typography
- Logo and favicon assets
- Bootstrap + Odoo SCSS variable overrides
- Light component refinements (buttons, inputs, statusbar)

Does NOT override core templates with `position=replace`.
Does NOT modify Odoo core source.
    """,
    'author': 'Özgür Rubber',
    'website': 'https://www.ozgurrubber.com',
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],
    'data': [
        'data/res_company_data.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('prepend', 'ozgur_branding/static/src/scss/_variables.scss'),
            'ozgur_branding/static/src/scss/_fonts.scss',
            'ozgur_branding/static/src/scss/branding.scss',
        ],
        'web.assets_frontend': [
            ('prepend', 'ozgur_branding/static/src/scss/_variables.scss'),
            'ozgur_branding/static/src/scss/_fonts.scss',
            'ozgur_branding/static/src/scss/branding.scss',
        ],
    },
    'post_init_hook': '_post_init_apply_branding',
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### 4.3 `hooks.py`

```python
"""Post-install hook: write logo + favicon to res.company on install."""
import base64
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)


def _post_init_apply_branding(env):
    """Apply logo and favicon to the main company after module install.

    This avoids hardcoding binary content in XML data files.
    Safe to re-run — only overwrites if the source asset file exists.
    """
    module_path = Path(__file__).parent
    img_dir = module_path / 'static' / 'img'

    company = env.ref('base.main_company', raise_if_not_found=False)
    if not company:
        _logger.warning("ozgur_branding: base.main_company not found, skipping logo apply.")
        return

    # Logo
    logo_candidates = ['logo.svg', 'logo_icon.png', 'logo_dark.png']
    for candidate in logo_candidates:
        logo_path = img_dir / candidate
        if logo_path.exists():
            try:
                with open(logo_path, 'rb') as f:
                    company.logo = base64.b64encode(f.read())
                _logger.info("ozgur_branding: applied %s to res.company.logo", candidate)
                break
            except Exception as e:
                _logger.warning("ozgur_branding: could not apply %s: %s", candidate, e)

    # Favicon
    favicon_path = img_dir / 'favicon.ico'
    if favicon_path.exists():
        try:
            with open(favicon_path, 'rb') as f:
                company.favicon = base64.b64encode(f.read())
            _logger.info("ozgur_branding: applied favicon.ico to res.company.favicon")
        except Exception as e:
            _logger.warning("ozgur_branding: could not apply favicon: %s", e)
```

### 4.4 `data/res_company_data.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Non-binary company-level settings can go here.
         Binary fields (logo, favicon) are set via post_init_hook (hooks.py).
         Add report header/footer customizations here later as needed. -->
    <data noupdate="0">
        <!-- placeholder; intentionally empty in Faz 1 -->
    </data>
</odoo>
```

### 4.5 `static/src/scss/_variables.scss` — **EN ÖNEMLİ DOSYA**

```scss
// =============================================================================
//  ÖZGÜR RUBBER — DESIGN TOKENS + BOOTSTRAP/ODOO VARIABLE OVERRIDE
//  This file is PREPENDED to both web.assets_backend and web.assets_frontend.
//  It must compile before Odoo's own SCSS, so $-variables here win.
// =============================================================================


// =============================================================================
//  LAYER 1 — DESIGN TOKENS (single source of truth)
// =============================================================================

// -------- Color: Navy (primary brand) --------
$ozg-navy-50:  #EAEEF4;
$ozg-navy-100: #C8D2E2;
$ozg-navy-200: #95A6BD;
$ozg-navy-400: #4D6890;
$ozg-navy-600: #1F3758;   // ★ PRIMARY
$ozg-navy-800: #142540;
$ozg-navy-900: #0B1729;

// -------- Color: Gold (brand accent) --------
$ozg-gold-50:  #FAF4E8;
$ozg-gold-100: #F0DDB5;
$ozg-gold-200: #E5C683;
$ozg-gold-400: #D5AD55;
$ozg-gold-600: #B8893A;   // ★ ACCENT
$ozg-gold-800: #8B6428;
$ozg-gold-900: #5C411B;

// -------- Color: Warm Stone (neutrals) --------
$ozg-stone-50:  #FAFAF7;
$ozg-stone-100: #F2EDE4;
$ozg-stone-200: #E5DED1;
$ozg-stone-400: #A8A095;
$ozg-stone-600: #6B655C;
$ozg-stone-800: #3F3B35;
$ozg-stone-900: #1F1D19;

// -------- Color: Semantic --------
$ozg-success: #2D7A4F;
$ozg-warning: #B8893A;     // gold reused as warning is intentional
$ozg-danger:  #B33A3A;
$ozg-info:    $ozg-navy-400;

// -------- Semantic aliases --------
$ozg-primary:           $ozg-navy-600;
$ozg-primary-hover:     $ozg-navy-800;
$ozg-primary-active:    $ozg-navy-900;
$ozg-text-primary:      $ozg-stone-900;
$ozg-text-secondary:    $ozg-stone-600;
$ozg-text-disabled:     $ozg-stone-400;
$ozg-bg-app:            #FFFFFF;
$ozg-bg-surface:        $ozg-stone-50;
$ozg-bg-surface-alt:    $ozg-stone-100;
$ozg-border-subtle:     $ozg-stone-200;
$ozg-border-strong:     $ozg-stone-400;

// -------- Typography --------
$ozg-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
$ozg-font-mono: 'JetBrains Mono', 'SF Mono', Monaco, Consolas, 'Liberation Mono', monospace;

// -------- Spacing scale (4px base) --------
$ozg-space-1:  4px;
$ozg-space-2:  8px;
$ozg-space-3:  12px;
$ozg-space-4:  16px;
$ozg-space-6:  24px;
$ozg-space-8:  32px;
$ozg-space-12: 48px;
$ozg-space-16: 64px;

// -------- Radius scale --------
$ozg-radius-sm: 4px;
$ozg-radius-md: 6px;
$ozg-radius-lg: 12px;


// =============================================================================
//  LAYER 2 — BOOTSTRAP VARIABLE OVERRIDE
//  These are Bootstrap 5 SCSS variables. Defining them here BEFORE Odoo's
//  bootstrap import means Bootstrap uses our values.
// =============================================================================

$primary:        $ozg-primary;
$secondary:      $ozg-stone-600;
$success:        $ozg-success;
$info:           $ozg-info;
$warning:        $ozg-warning;
$danger:         $ozg-danger;
$light:          $ozg-stone-50;
$dark:           $ozg-stone-900;

$body-bg:        $ozg-bg-app;
$body-color:     $ozg-text-primary;

$font-family-sans-serif: $ozg-font-sans;
$font-family-monospace:  $ozg-font-mono;
$font-family-base:       $ozg-font-sans;

$border-radius:    $ozg-radius-md;
$border-radius-sm: $ozg-radius-sm;
$border-radius-lg: $ozg-radius-lg;

$link-color:           $ozg-primary;
$link-hover-color:     $ozg-primary-hover;
$link-decoration:      none;
$link-hover-decoration: underline;


// =============================================================================
//  LAYER 3 — ODOO VARIABLE OVERRIDE
//  Odoo has its own $o-* SCSS variables. The complete list lives in:
//    addons/web/static/src/scss/primary_variables.scss
//    addons/web/static/src/scss/secondary_variables.scss
//
//  Below are the most commonly overridden ones. If a specific Odoo 19
//  variable isn't here, INSPECT the file above inside your Docker container
//  and add it. Do NOT guess at variable names that don't exist.
// =============================================================================

$o-brand-primary:        $ozg-primary;
$o-brand-odoo:           $ozg-primary;
$o-brand-secondary:      $ozg-gold-600;
$o-enterprise-color:     $ozg-primary;

$o-action:               $ozg-primary;
$o-view-background-color: $ozg-bg-app;
$o-webclient-background-color: $ozg-bg-app;
$o-main-text-color:      $ozg-text-primary;
$o-list-footer-bg-color: $ozg-stone-50;

$o-form-lightsecondary:  $ozg-stone-200;
$o-gray-100:             $ozg-stone-50;
$o-gray-200:             $ozg-stone-100;
$o-gray-300:             $ozg-stone-200;
$o-gray-400:             $ozg-stone-400;
$o-gray-500:             $ozg-stone-600;
$o-gray-600:             $ozg-stone-600;
$o-gray-700:             $ozg-stone-800;
$o-gray-800:             $ozg-stone-800;
$o-gray-900:             $ozg-stone-900;
```

> **⚠️ DİKKAT — Odoo 19 değişken adı doğrulaması:**
> Yukarıdaki `$o-*` değişkenlerinin hepsi Odoo 19'da bu adla mevcut olmayabilir.
> Modülü kurmadan önce Docker container içinde şu komutu çalıştır:
> ```bash
> docker compose exec odoo grep -rE '^\$o-' /usr/lib/python3/dist-packages/odoo/addons/web/static/src/scss/ 2>/dev/null | head -50
> ```
> Mevcut olmayan değişkenleri `_variables.scss`'ten **çıkar** (yorum satırı yapma — SCSS compile hatası verir). Çıkardıklarını `README.md > Bilinçli sapmalar` bölümüne not düş.

### 4.6 `static/src/scss/_fonts.scss`

```scss
// =============================================================================
//  Font face declarations — self-hosted Inter + JetBrains Mono
// =============================================================================

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('/ozgur_branding/static/fonts/Inter-Regular.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 500;
    font-display: swap;
    src: url('/ozgur_branding/static/fonts/Inter-Medium.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('/ozgur_branding/static/fonts/Inter-SemiBold.woff2') format('woff2');
}

@font-face {
    font-family: 'JetBrains Mono';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('/ozgur_branding/static/fonts/JetBrainsMono-Regular.woff2') format('woff2');
}

@font-face {
    font-family: 'JetBrains Mono';
    font-style: normal;
    font-weight: 500;
    font-display: swap;
    src: url('/ozgur_branding/static/fonts/JetBrainsMono-Medium.woff2') format('woff2');
}
```

### 4.7 `static/src/scss/branding.scss`

```scss
// =============================================================================
//  Light component refinements — applied AFTER Odoo's SCSS compiles.
//  Keep this file MINIMAL in Faz 1. No selector wars, no !important.
// =============================================================================

// Mono font for numeric fields — high-value win
.o_field_widget.o_field_monetary input,
.o_field_widget.o_field_float input,
.o_field_widget.o_field_integer input,
.o_field_widget.o_field_percentage input {
    font-family: $ozg-font-mono;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
}

// List view numeric cells — same treatment
.o_list_view .o_data_cell.o_list_number {
    font-family: $ozg-font-mono;
    font-variant-numeric: tabular-nums;
}

// Form group section title — give breathing room
// (Odoo's <separator string="..."/> renders as h3)
.o_form_view .o_horizontal_separator {
    margin-top: $ozg-space-6;
    margin-bottom: $ozg-space-3;
    padding-bottom: $ozg-space-2;
    border-bottom: 1px solid $ozg-border-subtle;
    font-weight: 500;
    color: $ozg-text-primary;
}

// Statusbar — subtle refinement
.o_statusbar_status .btn {
    border-radius: $ozg-radius-md;
}
```

### 4.8 `views/webclient_templates.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!--
        Faz 1 scope: hiçbir layout template'ini override etmiyoruz.
        Logo değişimi res.company.logo üzerinden post_init_hook ile yapılıyor;
        Odoo zaten login + navbar'da o alandan okuyor.

        Bu dosya, sonraki faz için (login arka planı, app launcher kart stili)
        hazır iskelet olarak duruyor. Şu an boş bırak — TODO bölümünde yer alıyor.
    -->
</odoo>
```

### 4.9 `static/description/index.html`

```html
<section class="container" style="padding: 24px;">
    <h1>Özgür Rubber Branding</h1>
    <p>Corporate visual identity for Özgür Rubber on Odoo 19.</p>
    <ul>
        <li>Navy / Gold / Warm Stone color system</li>
        <li>Inter + JetBrains Mono typography</li>
        <li>Logo &amp; favicon</li>
        <li>Token-first SCSS architecture</li>
    </ul>
</section>
```

### 4.10 `README.md` (modülün kendi README'si)

```markdown
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
<!-- Claude Code populates this section with anything it couldn't complete -->

## Bilinçli sapmalar
<!-- Any deviations from doctrine, with rationale -->
```

---

## 5. ASSET HAZIRLAMA — Adım Adım

### 5.1 Fontları indir

Google Fonts'tan Inter ve JetBrains Mono. Bunu yapmak için:

```bash
mkdir -p addons/ozgur_branding/static/fonts
cd addons/ozgur_branding/static/fonts

# Inter
for weight in "Regular:400" "Medium:500" "SemiBold:600"; do
    name="${weight%%:*}"
    num="${weight##*:}"
    # Bunny Fonts mirror — Google Fonts'a CSP/GDPR alternatifi
    curl -sLo "Inter-${name}.woff2" \
        "https://fonts.bunny.net/inter/files/inter-latin-${num}-normal.woff2"
done

# JetBrains Mono
for weight in "Regular:400" "Medium:500"; do
    name="${weight%%:*}"
    num="${weight##*:}"
    curl -sLo "JetBrainsMono-${name}.woff2" \
        "https://fonts.bunny.net/jetbrains-mono/files/jetbrains-mono-latin-${num}-normal.woff2"
done

ls -lh *.woff2
```

Her dosya >5KB olmalı. Daha küçükse indirme başarısız demektir → README'ye TODO yaz, kullanıcı manuel sağlayacak.

### 5.2 Logo dönüşümü

```bash
mkdir -p addons/ozgur_branding/static/img

# PDF → SVG
if command -v pdf2svg >/dev/null; then
    pdf2svg _brand_assets/BEYAZ.pdf addons/ozgur_branding/static/img/logo.svg
elif command -v inkscape >/dev/null; then
    inkscape _brand_assets/BEYAZ.pdf \
        --export-type=svg \
        --export-filename=addons/ozgur_branding/static/img/logo.svg
elif command -v magick >/dev/null || command -v convert >/dev/null; then
    # raster fallback
    CONVERT=$(command -v magick || command -v convert)
    $CONVERT -density 300 _brand_assets/BEYAZ.pdf \
        addons/ozgur_branding/static/img/logo.png
    echo "TODO: PDF→SVG converter not available, using PNG raster fallback." \
        >> addons/ozgur_branding/README.md
fi

# Dark variant
cp _brand_assets/logo_siyah_kaliteliden_düsüge.JPG \
    addons/ozgur_branding/static/img/logo_dark.png 2>/dev/null || true

# Favicon
cp _brand_assets/LOGO_ICON__1_.ico \
    addons/ozgur_branding/static/img/favicon.ico 2>/dev/null || true

# App store icon (256x256)
if command -v magick >/dev/null || command -v convert >/dev/null; then
    CONVERT=$(command -v magick || command -v convert)
    mkdir -p addons/ozgur_branding/static/description
    $CONVERT addons/ozgur_branding/static/img/favicon.ico \
        -resize 256x256 \
        addons/ozgur_branding/static/description/icon.png
fi
```

Her adım fail olursa: README'nin TODO bölümüne yaz, sessiz geçme.

---

## 6. DOĞRULAMA — Bittikten Sonra Çalıştır

```bash
# 1. Dosya ağacı doğru mu?
find addons/ozgur_branding -type f | sort

# 2. SCSS sentaks check (sass varsa)
if command -v sass >/dev/null; then
    sass --check addons/ozgur_branding/static/src/scss/_variables.scss
fi

# 3. Python sentaks check
python3 -m py_compile addons/ozgur_branding/__init__.py
python3 -m py_compile addons/ozgur_branding/__manifest__.py
python3 -m py_compile addons/ozgur_branding/hooks.py

# 4. Manifest okunabilir mi?
python3 -c "
import ast
with open('addons/ozgur_branding/__manifest__.py') as f:
    m = ast.literal_eval(f.read())
print('OK manifest:', m['name'], m['version'])
print('Assets keys:', list(m.get('assets', {}).keys()))
"

# 5. Odoo'yu restart et ve modülü install et
docker compose restart odoo
sleep 8
echo ">>> Open http://localhost:8069 → Apps → Update list → search 'Özgür' → Install"

# 6. Install logu izle
docker compose logs -f odoo | grep -i -E "ozgur|error|traceback"
```

---

## 7. ÇIKTI BEKLENTİSİ

Çalışmayı bitirdikten sonra şu raporu üret (terminale yaz, dosyaya kaydetme):

```
=== ozgur_branding — TAMAMLANDI ===

Oluşturulan dosyalar: <sayı>
Boyut toplamı: <KB>

Hazır olanlar:
- [✓/✗] Manifest
- [✓/✗] Hooks
- [✓/✗] _variables.scss (token + bootstrap + odoo override)
- [✓/✗] _fonts.scss
- [✓/✗] branding.scss
- [✓/✗] Logo SVG/PNG
- [✓/✗] Favicon
- [✓/✗] App icon 256x256
- [✓/✗] Inter fontları (5/5)
- [✓/✗] JetBrains Mono fontları (2/2)

Doğrulama:
- [✓/✗] Python compile
- [✓/✗] Manifest parse
- [✓/✗] Odoo container restart başarılı
- [✓/✗] Apps listesinde görünüyor

TODO sayısı: <N>
Bilinçli sapma sayısı: <N>

Sonraki adım:
- Odoo UI'da modülü install et
- Sonucu kontrol et (login + backend + navbar)
- TODO bölümünü gözden geçir
```

---

## 8. YAPMA LİSTESİ (bir kez daha)

- ❌ `addons/web/`, `addons/base/`, `addons/website/` altında **hiçbir** dosyaya dokunma.
- ❌ Repo kökündeki `docker-compose.yml`, `config/odoo.conf`, `README.md`'ye dokunma.
- ❌ Pip install, npm install, apt install — bu task'ta gereksiz.
- ❌ Database migration tetikleme.
- ❌ Mevcut data records'a SQL ile dokunma.
- ❌ Login template'ini Faz 1'de override etme (Faz 2 işi).
- ❌ Dark mode SCSS yazma.
- ❌ Yeni OWL component yaratma.
- ❌ Brief'te olmayan ekstra "iyileştirme" yapma. Scope creep yasak.

---

**Bitince commit at, push ETME** (kullanıcı PR olarak gözden geçirecek):

```bash
git add addons/ozgur_branding _brand_assets
git commit -m "feat(ozgur_branding): foundation module — tokens, fonts, palette, logo"
git status
```

Push'u kullanıcı yapacak.
