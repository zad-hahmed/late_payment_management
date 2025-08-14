# -*- coding: utf-8 -*-
{
    'name': 'Payment Management',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Manage overdue invoices with automatic and manual payment notices',
    'description': '''
        Late Payment Management System
        ============================

        Features:
        - Track late payment alerts on invoices
        - Manual action server for sending overdue notices
        - Automatic cron job for daily overdue checks
        - Custom wizard for personalized payment notices
        - Enhanced invoice views with late payment status
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'data/ir_actions_server.xml',
        'data/ir_cron.xml',
        'views/account_move_views.xml',
        'wizards/late_payment_notice_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
