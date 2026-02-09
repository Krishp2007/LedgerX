#LedgerX - Smart Digital Credit Ledger

LedgerX is a smart digital credit ledger designed for local shops to manage customers, track sales, and monitor credit transactions efficiently. It features automated reporting, QR code integrations, and offline recovery capabilities.

🚀 Features
Customer Management: Easily add, edit, and track customer credit histories.

Sales & Transactions: Record sales and payments with real-time balance updates.

Product Catalog: Manage inventory and stock levels with image support via Cloudinary.

Visual Reports: Insightful dashboards and visual representations of sales and customer data.

QR Code Integration: Generate and utilize QR codes for quick access and payment bridging.

Automated Emails: Transactional emails powered by Brevo.

🛠️ Tech Stack
Framework: Django 6.0

Database: PostgreSQL (via dj-database-url and psycopg2-binary)

Media Storage: Cloudinary (using django-cloudinary-storage)

Static Files: WhiteNoise

Email Service: Brevo (Sendinblue) API

Deployment: Optimized for Render.com

📋 Prerequisites
Before you begin, ensure you have the following installed:

Python 3.10+

PostgreSQL

A Cloudinary account (for media storage)

A Brevo API Key (for email services)

⚙️ Installation & Setup
Clone the repository:

Bash
git clone https://github.com/krishp2007/ledgerx.git
cd LedgerX
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Environment Variables: Create a .env file in the root directory (where manage.py is located) and add the following:

Code snippet
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/ledgerx
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
BREVO_API_KEY=your_brevo_key
DEFAULT_FROM_EMAIL=your_verified_email@example.com
Run Migrations:

Bash
python manage.py migrate
Start the Development Server:

Bash
python manage.py runserver
Access the application at http://127.0.0.1:8000/.

📂 Project Structure
accounts/: User authentication and shop profile management.

customers/: Customer records and credit profiles.

products/: Inventory and product tracking.

sales/: Transaction logic and payment history.

reports/: Dashboard and analytics.

qr/: QR code generation and payment bridging.

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Developed for local business empowerment.
