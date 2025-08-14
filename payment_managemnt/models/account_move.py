from odoo import models, fields, api
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    late_alert_sent = fields.Boolean(
        string='Late Alert Sent',
        default=False,
        help='Indicates if a late payment alert has been sent for this invoice'
    )

    is_overdue_invoice = fields.Boolean(
        string='Is Overdue Invoice',
        compute='_compute_is_overdue_invoice'
    )

    @api.depends('move_type', 'payment_state', 'state', 'invoice_date_due', 'late_alert_sent')
    def _compute_is_overdue_invoice(self):

        today = date.today()
        for record in self:
            record.is_overdue_invoice = (
                record.move_type == 'out_invoice' and
                record.payment_state != 'paid' and
                record.state == 'posted' and
                record.invoice_date_due and
                record.invoice_date_due < today and
                not record.late_alert_sent
            )

    @api.model
    def send_overdue_payment_notices(self, record_ids=None):

        try:
            if record_ids:
                all_selected = self.browse(record_ids)
                overdue_invoices = all_selected.filtered('is_overdue_invoice')
            else:
                overdue_invoices = self._get_overdue_invoices()

            if not overdue_invoices:
                message = "No overdue invoices found in selected records" if record_ids else "No overdue invoices found"
                return self._return_notification('Info', message, 'info')

            template_ref = 'payment_managemnt.overdue_payment_email_template'
            email_template = self.env.ref(template_ref, False)

            if not email_template:
                return self._return_notification('Error', f'Email template {template_ref} not found', 'danger')

            success_count = 0
            error_count = 0

            for invoice in overdue_invoices:
                try:
                    if not invoice.partner_id.email:
                        error_count += 1
                        continue

                    mail_values = {
                        'subject': f'Payment Reminder - Invoice {invoice.name}',
                        'body_html': self._get_email_body(invoice),
                        'email_to': invoice.partner_id.email,
                        'email_from': self.env.company.email or self.env.user.email,
                        'model': 'account.move',
                        'res_id': invoice.id,
                    }

                    mail = self.env['mail.mail'].create(mail_values)
                    mail.send()

                    invoice.write({'late_alert_sent': True})

                    invoice.message_post(
                        body=f"Late payment notice sent to {invoice.partner_id.email}",
                        subject="Late Payment Notice Sent"
                    )

                    success_count += 1

                except Exception:
                    error_count += 1
                    continue

            if success_count > 0:
                message = f'Successfully sent {success_count} overdue payment notices'
                if error_count > 0:
                    message += f' ({error_count} failed)'
                return self._return_notification('Success', message, 'success')
            else:
                return self._return_notification('Warning', f'No emails sent. {error_count} invoices had issues', 'warning')

        except Exception as e:
            return self._return_notification('Error', f'System error: {str(e)}', 'danger')

    def action_send_late_payment_notice(self):

        self.ensure_one()

        return {
            'name': 'Send Late Payment Notice',
            'type': 'ir.actions.act_window',
            'res_model': 'late.payment.notice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
                'default_email_to': self.partner_id.email,
            }
        }

    def _get_email_body(self, invoice):
        """Generate email body for overdue invoice"""
        customer_name = invoice.partner_id.name
        invoice_number = invoice.name
        due_date = invoice.invoice_date_due.strftime('%Y-%m-%d') if invoice.invoice_date_due else 'N/A'
        amount_due = f"{invoice.amount_residual:,.2f} {invoice.currency_id.name}"

        return f"""
        <div style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: #dc3545;">Payment Reminder</h2>
            <p>Dear {customer_name},</p>
            <p>This is a friendly reminder that your invoice <strong>{invoice_number}</strong> 
            with a due date of <strong>{due_date}</strong> is now overdue.</p>
            <p><strong>Outstanding Amount:</strong> {amount_due}</p>
            <p>Please arrange payment at your earliest convenience.</p>
            <p>Best regards,<br/>
            {invoice.company_id.name}</p>
        </div>
        """

    def _return_notification(self, title, message, notification_type):
        """Helper method to return notifications"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notification_type,
            }
        }

    @api.model
    def _get_overdue_invoices(self):
        """Get all overdue invoices that haven't been sent alerts"""
        today = date.today()
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', today),
            ('late_alert_sent', '=', False),
            ('state', '=', 'posted'),
        ]
        return self.search(domain)
