{
    'name': "Reamaze Integration",
    'summary': "Integración avanzada con Reamaze API",
    'version': '17.0.1.0.0',
    'category': 'Services',
    'author': "Esteban Viniegra | Pridecta",
    'depends': ['base', 'mail', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/reamaze_credentials_views.xml',
        'views/reamaze_conversation_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'icon': 'reamaze_odoo_integration/static/description/icon.png',
}