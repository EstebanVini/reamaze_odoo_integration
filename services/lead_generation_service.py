import logging
from odoo import models, fields, api # type: ignore

_logger = logging.getLogger(__name__)

class ReamazeLeadGenerationService(models.AbstractModel):
    _name = 'reamaze.lead.generation.service'
    _description = 'Servicio de Generación de Leads (Sin crear contactos)'

    def run_lead_generation(self):
        """ Procesa conversaciones y crea Leads en CRM """
        Conversation = self.env['reamaze.conversation']
        Lead = self.env['crm.lead']
        Partner = self.env['res.partner']

        # 1. Buscar conversaciones pendientes
        # Procesamos en lotes de 50 para no saturar si hay muchas acumuladas
        conversations = Conversation.search([
            ('estado_creacion_lead', '=', 'no_creado')
        ], limit=100)

        if not conversations:
            _logger.info("Reamaze Leads: No hay nada pendiente.")
            return

        # 2. Definir etiquetas de 'Lista Negra'
        blacklist_tags = [
            'Reply Inbox', 
            'Email', 
            'Facebook Comments', 
            'Instagram Comments'
        ]

        for conv in conversations:
            try:
                # Marcamos en proceso para evitar reentradas
                conv.write({'estado_creacion_lead': 'en_proceso'})

                # --- FILTRO DE ETIQUETAS ---
                # Obtenemos la lista de nombres de tags de esta conversación
                tag_names = conv.tag_ids.mapped('name')
                
                # Si alguna etiqueta prohibida está en la lista, omitimos
                if any(tag in blacklist_tags for tag in tag_names):
                    conv.write({'estado_creacion_lead': 'omitido'})
                    _logger.info(f"Reamaze: Lead omitido por tags {conv.slug}")
                    continue

                # --- VERIFICAR DUPLICADOS POR x_reamaze_id ---
                if conv.slug:
                    existing_lead = Lead.search([('x_reamaze_id', '=', conv.slug)], limit=1)
                    if existing_lead:
                        conv.write({
                            'estado_creacion_lead': 'creado',
                            'crm_lead_id': existing_lead.id
                        })
                        _logger.info(f"Reamaze: Lead duplicado encontrado {existing_lead.id} para {conv.slug}")
                        continue

                # --- BÚSQUEDA DE CONTACTO (SIN CREAR) ---
                partner_id = False
                if conv.author_email:
                    # Buscamos estrictamente por email exacto
                    existing_partner = Partner.search([('email', '=', conv.author_email)], limit=1)
                    if existing_partner:
                        partner_id = existing_partner.id
                        _logger.info(f"Reamaze: Contacto existente encontrado {existing_partner.name}")
                
                # --- PREPARACIÓN DE DATOS DEL LEAD ---
                # Obtenemos el primer tag para x_origen, si existe
                primer_tag = tag_names[0] if tag_names else False

                vals = {
                    'type': 'lead',
                    'active': True,
                    'name': conv.author_name or 'Prospecto Reamaze', # Título del Lead
                    'partner_id': False, # Solo si existía previamente
                    'user_id': 2,
                    
                    # Datos de contacto directos (se guardan en el Lead aunque no haya partner)
                    'contact_name': conv.author_name,
                    'email_from': conv.author_email or conv.author_name, # Fallback al nombre si no hay email (según tu indicación)
                    'mobile': conv.author_mobile,
                    'phone': conv.author_mobile,
                    
                    # Campos Personalizados (Asegúrate que existen en tu modelo crm.lead)
                    'x_reamaze_id': conv.slug,
                    'x_fecha_registro': conv.created_at_reamaze,
                    'x_link_conversacion': conv.perma_url,
                    'x_telefono': conv.author_mobile,
                    'x_origen': primer_tag,
                    'x_procedencia': 'vifac_nacional',
                    'x_titulo_conversacion': conv.subject or 'Sin Asunto',
                }

                # Intento de asignar al campo Phone Mobile Search si existe en tu BD
                # Como es un campo custom, verificamos si la columna existe para evitar errores
                if 'phone_mobile_search' in Lead._fields:
                     vals['phone_mobile_search'] = conv.author_mobile
                elif 'x_phone_mobile_search' in Lead._fields:
                     vals['x_phone_mobile_search'] = conv.author_mobile
                
                if conv.author_mobile:
                    vals['x_link_whatsapp'] = f"https://wa.me/{conv.author_mobile}"

                # --- CREACIÓN DEL LEAD ---
                new_lead = Lead.create(vals)

                # --- ACTUALIZACIÓN DE ESTADO ---
                conv.write({
                    'estado_creacion_lead': 'creado',
                    'crm_lead_id': new_lead.id
                })
                _logger.info(f"Reamaze: Lead creado exitosamente {new_lead.id} para {conv.slug}")

            except Exception as e:
                _logger.error(f"Reamaze: Error creando lead para {conv.slug}: {str(e)}")
                conv.write({'estado_creacion_lead': 'error'})