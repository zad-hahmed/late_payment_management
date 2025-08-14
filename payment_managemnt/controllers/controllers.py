# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentManagemnt(http.Controller):
#     @http.route('/payment_managemnt/payment_managemnt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_managemnt/payment_managemnt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_managemnt.listing', {
#             'root': '/payment_managemnt/payment_managemnt',
#             'objects': http.request.env['payment_managemnt.payment_managemnt'].search([]),
#         })

#     @http.route('/payment_managemnt/payment_managemnt/objects/<model("payment_managemnt.payment_managemnt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_managemnt.object', {
#             'object': obj
#         })

