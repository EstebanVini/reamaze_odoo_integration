import requests
import logging
from datetime import datetime, timedelta
from dateutil import parser
import json
from odoo import models, api # type: ignore

_logger = logging.getLogger(__name__)

class ReamazeConversationsService(models.AbstractModel):
    _name = 'reamaze.conversations.service'
    _description = 'Servicio de Sincronización de Conversaciones'

    def run_import(self):
        """ Método punto de entrada para Cron o Botón """
        params = self.env['ir.config_parameter'].sudo()
        brand = params.get_param('reamaze.brand')
        email = params.get_param('reamaze.login_email')
        token = params.get_param('reamaze.api_token')

        if not all([brand, email, token]):
            _logger.warning("Reamaze: Credenciales faltantes.")
            return

        base_url = f"https://{brand}.reamaze.com/api/v1/conversations"
        
        # 1. Definir el Límite de Tiempo (Últimos 2 días)
        # Usamos una fecha "naive" (sin zona horaria) porque Odoo guarda así en BD
        lookback_days = 2
        limit_date = datetime.utcnow() - timedelta(days=lookback_days)
        
        # Para la API, formatedamos la fecha como string ISO
        formatted_date_api = limit_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        page = 1
        total_imported = 0
        stop_pagination = False # Bandera para detener el bucle while

        _logger.info(f"Reamaze: Iniciando descarga. Límite de fecha: {limit_date}")

        while not stop_pagination:
            # Nota: Mantenemos el filtro 'q' en la API por si acaso ayuda, 
            # pero confiaremos en nuestra validación manual.
            query_params = {
                "q": f"created_at:[{formatted_date_api} TO *]",
                "data": "true",
                "page": page,
                "sort": "created_at" # Intentamos forzar el orden
            }

            try:
                _logger.info(f"Reamaze: Descargando página {page}...")
                response = requests.get(
                    base_url, 
                    auth=(email, token), 
                    params=query_params,
                    headers={"Accept": "application/json"},
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                conversations = data.get('conversations', [])
                
                if not conversations:
                    _logger.info("Reamaze: No hay más conversaciones en la página.")
                    break
                
                # Procesamos el lote actual
                for item in conversations:
                    # 2. VALIDACIÓN DE FECHA (CIRCUIT BREAKER)
                    created_at_str = item.get('created_at')
                    item_date = self._parse_date(created_at_str)

                    # Si la fecha del item es válida y es MENOR que mi fecha límite...
                    if item_date and item_date < limit_date:
                        _logger.info(f"Reamaze: Se alcanzó una conversación antigua ({item_date}). Deteniendo sincronización.")
                        stop_pagination = True
                        break # Rompe el for

                    # Si la fecha está bien, procesamos
                    self._process_single_conversation(item)
                    total_imported += 1
                
                # Si se activó la bandera dentro del for, rompemos el while también
                if stop_pagination:
                    break

                page += 1
                
                # Límite de seguridad técnico
                if page > 150: 
                    _logger.warning("Reamaze: Límite técnico de 150 páginas alcanzado.")
                    break

            except Exception as e:
                _logger.error(f"Reamaze Error en página {page}: {str(e)}")
                break
        
        _logger.info(f"Reamaze: Sincronización finalizada. Total procesados: {total_imported}")

    def _process_single_conversation(self, item):
        """ Lógica de guardado para el modelo extendido """
        Conversation = self.env['reamaze.conversation']
        import json  # Importación local para asegurar disponibilidad

        try:
            slug = item.get('slug')
            if not slug:
                return

            # 1. Procesar Relaciones (Tags y Followers)
            tag_records = self._get_or_create_tags(item.get('tag_list', []))
            follower_records = self._get_or_create_followers(item.get('followers', []))

            # 2. Extraer Sub-diccionarios con seguridad
            # Usamos .get() or {} para evitar errores si algún campo viene null
            message_data = item.get('message') or {}
            category_data = item.get('category') or {}
            author_data = item.get('author') or {}
            assignee_data = item.get('assignee') or {}
            last_customer_msg = item.get('last_customer_message') or {}
            last_staff_msg = item.get('last_staff_message') or {}

            # 3. Procesar campos JSON (convertir dict a string)
            # ensure_ascii=False permite guardar tildes y caracteres especiales correctamente
            data_json = json.dumps(item.get('data'), ensure_ascii=False) if item.get('data') else False
            author_data_json = json.dumps(author_data.get('data'), ensure_ascii=False) if author_data.get('data') else False
            assignee_data_json = json.dumps(assignee_data.get('data'), ensure_ascii=False) if assignee_data.get('data') else False

            # 4. Mapeo completo de datos
            vals = {
                # --- Identificación y Contenido Principal ---
                'slug': slug,
                'subject': item.get('subject') or 'Sin Asunto',
                'display_subject': item.get('display_subject'),
                'body': message_data.get('body') or '', # Cuerpo principal (usualmente el primer mensaje)
                'data': data_json,
                'hold_until': item.get('hold_until'), # Guardamos como Char según tu modelo

                # --- Fechas ---
                'created_at_reamaze': self._parse_date(item.get('created_at')),
                'updated_at_reamaze': self._parse_date(item.get('updated_at')),

                # --- Datos Reamaze ---
                'origin': item.get('origin'),
                'status': item.get('status'),
                'perma_url': item.get('perma_url'),

                # --- Categoría ---
                'category_name': category_data.get('name'),
                'category_slug': category_data.get('slug'),
                'category_email': category_data.get('email'),
                'category_channel': category_data.get('channel'),
                'category_settings_display_html_email': category_data.get('settings_display_html_email'),

                # --- Datos del Autor ---
                'author_id': author_data.get('id'),
                'author_name': author_data.get('name'),
                'author_email': author_data.get('email'),
                'author_mobile': author_data.get('mobile'),
                'author_twitter': author_data.get('twitter'),
                'author_facebook': author_data.get('facebook'),
                'author_instagram': author_data.get('instagram'),
                'author_friendly_name': author_data.get('friendly_name'),
                'author_display_name': author_data.get('display_name'),
                'author_data': author_data_json,

                # --- Datos del Asignado ---
                'assignee_id': assignee_data.get('id'),
                'assignee_name': assignee_data.get('name'),
                'assignee_email': assignee_data.get('email'),
                'assignee_mobile': assignee_data.get('mobile'),
                'assignee_twitter': assignee_data.get('twitter'),
                'assignee_facebook': assignee_data.get('facebook'),
                'assignee_instagram': assignee_data.get('instagram'),
                'assignee_friendly_name': assignee_data.get('friendly_name'),
                'assignee_display_name': assignee_data.get('display_name'),
                'assignee_data': assignee_data_json,

                # --- Últimos Mensajes ---
                'last_customer_message_body': last_customer_msg.get('body'),
                'last_customer_message_created_at': self._parse_date(last_customer_msg.get('created_at')),
                'last_staff_message_body': last_staff_msg.get('body'),
                'last_staff_message_created_at': self._parse_date(last_staff_msg.get('created_at')),

                # --- Detalles del Mensaje ---
                'message_body': message_data.get('body'),
                'message_origin_id': message_data.get('origin_id'),
                'message_count': item.get('message_count'),

                # --- Relaciones ---
                'tag_ids': [(6, 0, tag_records.ids)],
                'follower_ids': [(6, 0, follower_records.ids)],
            }

            # 5. Guardar en Base de Datos (Upsert)
            existing = Conversation.search([('slug', '=', slug)], limit=1)
            if existing:
                existing.write(vals)
            else:
                Conversation.create(vals)

        except Exception as e_inner:
            # Imprimimos el error pero no detenemos todo el proceso
            _logger.error(f"Reamaze: Falló al importar {item.get('slug')}: {str(e_inner)}")

    def _parse_date(self, date_str):
        if not date_str: return False
        try:
            dt = parser.parse(date_str)
            return dt.replace(tzinfo=None)
        except: return False

    def _get_or_create_tags(self, tag_list):
        TagModel = self.env['reamaze.conversation.tag']
        ids = []
        if not tag_list: return TagModel.browse()
        for tag_name in tag_list:
            if not tag_name: continue
            tag = TagModel.search([('name', '=', tag_name)], limit=1)
            if not tag:
                tag = TagModel.create({'name': tag_name})
            ids.append(tag.id)
        return TagModel.browse(ids)

    def _get_or_create_followers(self, followers_list):
        FollowerModel = self.env['reamaze.conversation.follower']
        ids = []
        if not followers_list: return FollowerModel.browse()
        for f_data in followers_list:
            r_id = f_data.get('id')
            if not r_id: continue
            follower = FollowerModel.search([('reamaze_id', '=', r_id)], limit=1)
            vals = {
                'name': f_data.get('name'),
                'email': f_data.get('email'),
                'reamaze_id': r_id,
                'data': json.dumps(f_data.get('data'), ensure_ascii=False) if f_data.get('data') else False,
                'twitter': f_data.get('twitter'),
                'facebook': f_data.get('facebook'),
                'instagram': f_data.get('instagram'),
                'mobile': f_data.get('mobile'),
                'friendly_name': f_data.get('friendly_name'),
                'display_name': f_data.get('display_name'),
                'is_staff': f_data.get('is_staff', False),
                'is_customer': f_data.get('is_customer', False),
                'is_bot': f_data.get('is_bot', False),
            }
            if follower:
                follower.write(vals)
            else:
                follower = FollowerModel.create(vals)
            ids.append(follower.id)
        return FollowerModel.browse(ids)