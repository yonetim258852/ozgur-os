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
