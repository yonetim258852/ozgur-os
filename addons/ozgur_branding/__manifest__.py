{
    'name': 'Özgür Rubber Branding',
    'version': '19.0.1.0.0',
    'category': 'Customization',
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
        # NOTE: The `website` module overrides `_get_active_addons_list` to
        # filter `web.assets_frontend` per website. Non-website-bound modules
        # (like this one) get filtered out for public/login pages. Declaring
        # the same files under `website.assets_frontend` makes the branding
        # reach login + portal + website-public surfaces too.
        'website.assets_frontend': [
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
