import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    vkn_tckn = fields.Char(string="VKN/TCKN", size=11, index=True)
    vergi_dairesi = fields.Char(string="Vergi Dairesi")

    @api.constrains("vkn_tckn")
    def _check_vkn_tckn(self):
        for partner in self:
            value = partner.vkn_tckn
            if not value:
                continue
            if not re.fullmatch(r"\d{10}|\d{11}", value):
                raise ValidationError(
                    _("VKN/TCKN sadece rakam icermeli; 10 hane (VKN) veya 11 hane (TCKN) olmalidir.")
                )
