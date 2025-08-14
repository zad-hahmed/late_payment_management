from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LatePaymentNoticeWizard(models.TransientModel):
    _name = 'late.payment.notice.wizard'
    _description = 'Late Payment Notice Wizard'

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        required=True,
        readonly=True
    )

    email_to = fields.Char(
        string='Send To',
        required=True,
        help='Email address to send the overdue notice'
    )

    message_body = fields.Html(
        string='Message',
        required=True,
        help='Custom message for the overdue payment notice'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        invoice_id = self.env.context.get('default_invoice_id')
        if invoice_id:
            invoice = self.env['account.move'].browse(invoice_id)

            if 'email_to' in fields_list and invoice.partner_id.email:
                res['email_to'] = invoice.partner_id.email

            if 'message_body' in fields_list:
                res['message_body'] = self._get_default_message(invoice)

        return res

    def _get_default_message(self, invoice):
        customer_name = invoice.partner_id.name
        invoice_number = invoice.name
        due_date = invoice.invoice_date_due.strftime('%Y-%m-%d') if invoice.invoice_date_due else 'N/A'
        amount_due = f"{invoice.amount_residual:,.2f} {invoice.currency_id.name}"

        message = f"""
        <div style="font-family: Arial, sans-serif; margin: 20px;">
            <p>Dear {customer_name},</p>

            <p>We hope this message finds you well.</p>

            <p>This is a friendly reminder that your invoice <strong>{invoice_number}</strong> 
            with a due date of <strong>{due_date}</strong> is now overdue.</p>

            <p><strong>Outstanding Amount:</strong> {amount_due}</p>

            <p>We kindly request that you arrange payment at your earliest convenience. 
            If you have already made this payment, please disregard this notice.</p>

            <p>If you have any questions or concerns regarding this invoice, 
            please don't hesitate to contact us.</p>

            <p>Thank you for your prompt attention to this matter.</p>

            <p>Best regards,<br/>
            Accounts Receivable Department</p>
        </div>
        """

        return message

    def action_send_notice(self):
        self.ensure_one()

        if not self.email_to:
            raise ValidationError("Email address is required")

        try:
            mail_values = {
                'subject': f'Payment Reminder - Invoice {self.invoice_id.name}',
                'body_html': self.message_body,
                'email_to': self.email_to,
                'email_from': self.env.company.email or self.env.user.email,
                'model': 'account.move',
                'res_id': self.invoice_id.id,
            }

            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

            self.invoice_id.write({'late_alert_sent': True})

            self.invoice_id.message_post(
                body=f"Late payment notice sent to {self.email_to}",
                subject="Late Payment Notice Sent"
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Late payment notice sent successfully to {self.email_to}',
                    'type': 'success',
                }
            }

        except Exception as e:
            raise ValidationError(f"Failed to send email: {str(e)}")
