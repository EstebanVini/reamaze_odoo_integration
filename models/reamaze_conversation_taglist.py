from odoo import fields, models # type: ignore

class ReamazeTag(models.Model):
    _name = 'reamaze.conversation.tag'
    _description = 'Etiqueta de Reamaze'

    name = fields.Char(string="Nombre Etiqueta", required=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre de la etiqueta debe ser único.')
    ]