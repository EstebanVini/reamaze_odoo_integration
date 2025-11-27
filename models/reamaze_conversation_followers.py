from odoo import fields, models

class ReamazeFollower(models.Model):
    _name = 'reamaze.conversation.follower'
    _description = 'Seguidor de Conversación Reamaze'
    _rec_name = 'name'

    # ID del usuario en Reamaze (ej. 776593597)
    reamaze_id = fields.Integer(string="Reamaze ID", index=True, required=True)
    name = fields.Char(string="Nombre")
    email = fields.Char(string="Email")
    
    # Relación con conversaciones (Many2many es lo ideal, un follower puede estar en varias)
    conversation_ids = fields.Many2many(
        'reamaze.conversation', 
        string="Conversaciones"
    )

    _sql_constraints = [
        ('reamaze_id_uniq', 'unique (reamaze_id)', 'El ID de seguidor debe ser único.')
    ]