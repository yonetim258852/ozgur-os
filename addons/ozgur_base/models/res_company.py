from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mersis_no = fields.Char(string="MERSIS No", size=16)
    kep_adresi = fields.Char(string="KEP Adresi")
    sicil_no = fields.Char(string="Ticaret Sicil No")
