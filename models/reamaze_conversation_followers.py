from odoo import fields, models # type: ignore

class ReamazeFollower(models.Model):
    _name = 'reamaze.conversation.follower'
    _description = 'Seguidor de Conversación Reamaze'
    _rec_name = 'name'

    # ID del usuario en Reamaze (ej. 776593597)
    reamaze_id = fields.Integer(string="Reamaze ID", index=True, required=True)
    name = fields.Char(string="Nombre")
    email = fields.Char(string="Email")
    data = fields.Text(string="Data")
    twitter = fields.Char(string="Twitter")
    facebook = fields.Char(string="Facebook")
    instagram = fields.Char(string="Instagram")
    mobile = fields.Char(string="Mobile")
    friendly_name = fields.Char(string="Friendly Name")
    display_name = fields.Char(string="Display Name")
    is_staff = fields.Boolean(string="Is Staff", default=False)
    is_customer = fields.Boolean(string="Is Customer", default=False)
    is_bot = fields.Boolean(string="Is Bot", default=False)

    # Relación con conversaciones (Many2many es lo ideal, un follower puede estar en varias)
    conversation_ids = fields.Many2many(
        'reamaze.conversation', 
        string="Conversaciones"
    )

    _sql_constraints = [
        ('reamaze_id_uniq', 'unique (reamaze_id)', 'El ID de seguidor debe ser único.')
    ]