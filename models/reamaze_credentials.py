from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reamaze_brand = fields.Char(
        string="Brand", config_parameter='reamaze.brand',
        help="El subdominio de tu URL de Reamaze (ej. 'vifac')"
    )
    reamaze_login_email = fields.Char(
        string="Login Email", config_parameter='reamaze.login_email'
    )
    reamaze_api_token = fields.Char(
        string="API Token", config_parameter='reamaze.api_token'
    )