{
    'name': "Reamaze Integration",
    'summary': "Integración avanzada con Reamaze API",
    'version': '17.0.1.0.0',
    'category': 'Services',
    'author': "Odoo Expert",
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/reamaze_credentials_views.xml',
        'views/reamaze_conversation_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}