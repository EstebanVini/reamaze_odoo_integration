from odoo import fields, models # type: ignore

class ReamazeConversation(models.Model):
    _name = 'reamaze.conversation'
    _description = 'Conversación Reamaze'
    _rec_name = 'subject'
    _order = 'created_at_reamaze desc'

    slug = fields.Char(string="Slug", required=True, index=True)
    subject = fields.Char(string="Asunto")
    body = fields.Text(string="Cuerpo del Mensaje")
    data = fields.Text(string="Metadatos de la Conversación en formato JSON")
    hold_until = fields.Char(string="Poner en Espera Hasta")
    display_subject = fields.Char(string="Asunto para Mostrar")
    
    # Fechas
    created_at_reamaze = fields.Datetime(string="Creado en")
    updated_at_reamaze = fields.Datetime(string="Actualizado en")
    
    # Datos Reamaze
    origin = fields.Integer(string="Origen")
    status = fields.Integer(string="Estado")
    perma_url = fields.Char(string="URL Permanente")

    # Categoría|
    category_name = fields.Char(string="Categoría")
    category_slug = fields.Char(string="Slug Categoría")
    category_email = fields.Char(string="Email Categoría")
    category_channel = fields.Integer(string="Canal Categoría")
    category_settings_display_html_email = fields.Char(string="Configuración Display HTML Email")

    # --- Datos del Autor ---
    author_id = fields.Integer(string="ID Autor")
    author_name = fields.Char(string="Nombre Autor")
    author_email = fields.Char(string="Email Autor")
    author_mobile = fields.Char(string="Móvil Autor")
    author_twitter = fields.Char(string="Twitter Autor")
    author_facebook = fields.Char(string="Facebook Autor")
    author_instagram = fields.Char(string="Instagram Autor")
    author_friendly_name = fields.Char(string="Nombre Amigable Autor")
    author_display_name = fields.Char(string="Nombre para Mostrar Autor")
    author_data = fields.Text(string="Datos Autor (JSON)")
    # ----------------------------------

    # --- Datos del Asignado ---
    assignee_id = fields.Integer(string="ID Asignado")
    assignee_name = fields.Char(string="Nombre Asignado")
    assignee_email = fields.Char(string="Email Asignado")
    assignee_mobile = fields.Char(string="Móvil Asignado")
    assignee_twitter = fields.Char(string="Twitter Asignado")
    assignee_facebook = fields.Char(string="Facebook Asignado")
    assignee_instagram = fields.Char(string="Instagram Asignado")
    assignee_friendly_name = fields.Char(string="Nombre Amigable Asignado")
    assignee_display_name = fields.Char(string="Nombre para Mostrar Asignado")
    assignee_data = fields.Text(string="Datos Asignado (JSON)")
    # ----------------------------------


    #Last custommer message 
    last_customer_message_body = fields.Text(string="Cuerpo del Último Mensaje del Cliente")
    last_customer_message_created_at = fields.Datetime(string="Creado en del Último Mensaje del Cliente")

    last_staff_message_body = fields.Text(string="Cuerpo del Último Mensaje del Staff")
    last_staff_message_created_at = fields.Datetime(string="Creado en del Último Mensaje del Staff")

    message_body = fields.Text(string="Cuerpo del Mensaje")
    message_origin_id = fields.Char(string="ID Origen del Mensaje")
    message_count = fields.Integer(string="Cantidad de Mensajes")


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