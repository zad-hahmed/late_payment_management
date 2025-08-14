Late Payment Management - Odoo 18
Automated overdue invoice notifications with custom messaging for Odoo 18.

 Features

- Automatic detection of overdue customer invoices
- Manual and scheduled email notifications 
- Customizable payment reminder wizard
- Server actions for bulk processing
- Enhanced invoice views with late payment tracking

 Installation

1. Clone this repository into your Odoo addons directory
2. Restart Odoo server
3. Go to Apps → Update Apps List
4. Search for "Payment Management" and install

Usage

- Manual: Select overdue invoices → Actions → Send Overdue Payment Notices
- Individual: Open overdue invoice → Click "Send Late Payment Notice" button
- Automatic: Cron job runs daily at 8 AM

Requirements

- Odoo 18.0
- account module
- mail module
