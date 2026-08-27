# SwiftPay 💳

SwiftPay is a modern, high-performance payment gateway designed for merchants and developers. Built on a robust Django backend and a lightweight Vanilla JavaScript frontend, it offers secure payment processing, real-time webhooks, and comprehensive merchant tooling.

## 🚀 Key Features

### Architecture & Reliability
- **CQRS & Event Sourcing**: Payment states and merchant balances are strictly decoupled using Command Query Responsibility Segregation (CQRS) and an append-only event log for perfect financial auditability.
- **Transactional Outbox**: Guarantees 100% reliable webhook delivery by committing webhook tasks in the same atomic database transaction as the payment state change. No split-brain failures.

### Security
- **Hardened Webhooks**: Outbound webhooks are protected against Server-Side Request Forgery (SSRF) via DNS resolution and strict IP validation (blocking private/loopback CIDRs).
- **HMAC Signatures**: Every webhook payload is cryptographically signed using HMAC SHA-256, allowing merchants to confidently verify the origin of events.
- **API Key Security**: API keys are securely hashed using Django's PBKDF2 algorithm before storage. `Key_Secret` is only shown once during generation.

### Merchant Dashboard
- **Real-time Analytics**: View available balances, pending settlements, and recent transactions.
- **Modern Authentication**: Secure access via Google OAuth or traditional Email/Password powered by JWTs.
- **Automated Validation**: Strict regex validation for PAN, GST, IFSC, and Bank Account numbers to ensure regulatory compliance.

## 🛠 Tech Stack

- **Backend:** Python, Django, Django REST Framework, PostgreSQL
- **Frontend:** HTML5, Vanilla JavaScript, CSS (Custom Design System)
- **Authentication:** SimpleJWT, Google OAuth2
- **Integrations:** Twilio (OTP Verification)

## 💻 Local Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Twilio Account (for OTPs)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/swiftpay.git
   cd swiftpay
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your configurations:
   ```env
   DEBUG=True
   SECRET_KEY=your_django_secret_key
   
   # Database
   DB_NAME=swiftpay_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # Authentication & Integrations
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_FROM_NUMBER=your_twilio_number
   ```

5. **Run Database Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   *The merchant dashboard will be available at `http://127.0.0.1:8000/`*

## 📖 API Documentation

To accept payments, merchants need to generate an API key via the dashboard and include it in the `Authorization` header of their requests.

```bash
curl -X POST https://api.swiftpay.local/payments/ \
  -H "Authorization: Basic <base64_encoded_key_id:key_secret>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100.50",
    "currency": "INR",
    "reference": "order_12345"
  }'
```



