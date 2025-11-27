import requests
import logging
from datetime import datetime, timedelta
from odoo import models, api

_logger = logging.getLogger(__name__)

class ReamazeConversationsService(models.AbstractModel):
    _name = 'reamaze.conversations.service'
    _description = 'Servicio de Sincronización de Conversaciones'

    def run_import(self):
        """ Método punto de entrada para Cron o Botón """
        # 1. Obtener Credenciales
        params = self.env['ir.config_parameter'].sudo()
        brand = params.get_param('reamaze.brand')
        email = params.get_param('reamaze.login_email')
        token = params.get_param('reamaze.api_token')

        if not all([brand, email, token]):
            _logger.warning("Reamaze: Credenciales faltantes.")
            return

        # 2. Configurar Request
        base_url = f"https://{brand}.reamaze.com/api/v1/conversations"
        
        # Filtro de tiempo (últimas 24h para demo)
        # En producción podrías guardar un 'last_sync_date' en ir.config_parameter
        yesterday = datetime.utcnow() - timedelta(days=1)
        formatted_date = yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        query_params = {
            "q": f"created_at:[{formatted_date} TO *]",
            "data": "true"
        }

        try:
            response = requests.get(
                base_url, 
                auth=(email, token), 
                params=query_params,
                headers={"Accept": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            conversations = data.get('conversations', [])
            
            _logger.info(f"Reamaze: Procesando {len(conversations)} conversaciones.")
            self._sync_conversations(conversations)

        except Exception as e:
            _logger.error(f"Reamaze Error: {str(e)}")

    def _sync_conversations(self, conversations_data):
        Conversation = self.env['reamaze.conversation']
        
        for item in conversations_data:
            slug = item.get('slug')
            if not slug:
                continue

            # 1. Procesar Tags (Strings -> Registros)
            tag_records = self._get_or_create_tags(item.get('tag_list', []))

            # 2. Procesar Followers (Dicts -> Registros)
            follower_records = self._get_or_create_followers(item.get('followers', []))

            # 3. Preparar valores principales
            message_data = item.get('message', {}) or {}
            category_data = item.get('category', {}) or {}
            
            vals = {
                'slug': slug,
                'subject': item.get('subject'),
                'body': message_data.get('body'),
                'created_at_reamaze': item.get('created_at'),
                'updated_at_reamaze': item.get('updated_at'),
                'origin': item.get('origin'),
                'status': item.get('status'),
                'perma_url': item.get('perma_url'),
                'category_name': category_data.get('name'),
                # Many2many comandos (6, 0, ids) reemplaza la lista actual
                'tag_ids': [(6, 0, tag_records.ids)], 
                'follower_ids': [(6, 0, follower_records.ids)],
            }

            # 4. Upsert (Buscar y crear o escribir)
            existing = Conversation.search([('slug', '=', slug)], limit=1)
            if existing:
                existing.write(vals)
            else:
                Conversation.create(vals)

    def _get_or_create_tags(self, tag_list):
        """ Recibe ['Tag1', 'Tag2'] y devuelve un recordset de tags """
        TagModel = self.env['reamaze.conversation.tag']
        ids = []
        for tag_name in tag_list:
            # Buscar tag insensible a mayúsculas/minúsculas si prefieres
            tag = TagModel.search([('name', '=', tag_name)], limit=1)
            if not tag:
                tag = TagModel.create({'name': tag_name})
            ids.append(tag.id)
        return TagModel.browse(ids)

    def _get_or_create_followers(self, followers_list):
        """ Recibe lista de diccionarios de followers y devuelve recordset """
        FollowerModel = self.env['reamaze.conversation.follower']
        ids = []
        for f_data in followers_list:
            r_id = f_data.get('id')
            if not r_id:
                continue
            
            follower = FollowerModel.search([('reamaze_id', '=', r_id)], limit=1)
            vals = {
                'name': f_data.get('name'),
                'email': f_data.get('email'),
                'reamaze_id': r_id
            }
            
            if follower:
                follower.write(vals)
            else:
                follower = FollowerModel.create(vals)
            
            ids.append(follower.id)
        return FollowerModel.browse(ids)