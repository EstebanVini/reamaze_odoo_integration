from odoo import fields, models

class ReamazeConversation(models.Model):
    _name = 'reamaze.conversation'
    _description = 'Conversación Reamaze'
    _rec_name = 'subject'
    _order = 'created_at_reamaze desc'

    slug = fields.Char(string="Slug", required=True, index=True)
    subject = fields.Char(string="Asunto")
    body = fields.Text(string="Cuerpo del Mensaje")
    
    # Fechas
    created_at_reamaze = fields.Datetime(string="Creado en")
    updated_at_reamaze = fields.Datetime(string="Actualizado en")
    
    # Datos Reamaze
    origin = fields.Integer(string="Origen")
    status = fields.Integer(string="Estado")
    perma_url = fields.Char(string="URL Permanente")
    category_name = fields.Char(string="Categoría")

    # --- NUEVOS CAMPOS QUE FALTABAN ---
    author_name = fields.Char(string="Nombre Autor")
    author_email = fields.Char(string="Email Autor")
    author_mobile = fields.Char(string="Móvil Autor")
    # ----------------------------------

    # Relaciones
    tag_ids = fields.Many2many(
        'reamaze.conversation.tag', 
        string="Etiquetas"
    )
    follower_ids = fields.Many2many(
        'reamaze.conversation.follower', 
        string="Seguidores"
    )

    _sql_constraints = [
        ('slug_uniq', 'unique (slug)', 'El slug debe ser único.')
    ]