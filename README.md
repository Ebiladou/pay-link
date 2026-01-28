# PayLink

**PayLink** is a modern payment link service that simplifies receiving payments online. It enables users to create shareable payment links that can be sent to customers, clients, or anyone who needs to send money. Instead of complex payment forms or invoices, users can generate a simple link and share it via email, messaging, or social media.

PayLink integrates with **Paystack** to handle secure payment transactions. Users can:

- **Create Payment Links** - Generate unique, shareable links for receiving payments
- **Multiple Link Types**:
  - **Closed Links** - Pre-configured with a fixed amount for a specific recipient
  - **Open Links** - Flexible links where customers can enter custom amounts
  - **Recurring Links** - Setup automatic payment subscriptions
- **Instant Payments** - Customers pay directly through the link without creating an account
- **Payment Tracking** - Monitor all payments, refunds, and transaction history

## Technical Overview

PayLink is built with a modern, scalable architecture:

- **FastAPI Backend** - High-performance Python API framework
- **Asynchronous Email Processing** - RabbitMQ-based queue for instant user responses
- **PostgreSQL Database** - Reliable data persistence with async support
- **Payment Integration** - Secure integration with Paystack
- **User Authentication** - JWT-based secure authentication with refresh tokens
- **Production Ready** - Dockerized, logged, and optimized for scale -> # in view

## Features

- 🔐 **User Authentication** - Secure signup, login, and password reset
- 💳 **Payment Processing** - Integration with Paystack for secure payments
- 🔗 **Flexible Link Creation** - Multiple link types (closed, open, recurring, etc.)
- 📊 **Transaction Tracking** - Real-time payment status and history
- 📧 **Async Email Queue** - RabbitMQ-based email processing (non-blocking)
- 🔄 **Background Workers** - Email sending in separate threads
- 📝 **Centralized Logging** - Environment-aware logging with file rotation
- 🗄️ **PostgreSQL Database** - Using SQLModel and AsyncPG for async database operations
- 🎯 **RESTful API** - Clean API endpoints for link and payment management
- 🔒 **Security First** - HTTPS, CORS protection, secure token handling

## Architecture

### Email Queue System

The application uses RabbitMQ to queue emails asynchronously:

```
User Request (FastAPI Main Thread)
    ↓
queue_email() → RabbitMQ Queue (instant, non-blocking)
    ↓
Return response to user immediately
    
Meanwhile (Background Worker Thread)
    ↓
start_email_worker() listens on RabbitMQ
    ↓
Process message → Send email via MailerSend
    ↓
Acknowledge message to queue
```

## Prerequisites

- Python 3.12+
- PostgreSQL
- RabbitMQ
- pip/virtualenv

## Installation

### 1. Clone the Repository
```bash
git clone git@github.com:Ebiladou/pay-link.git
cd pay-link
```

### 2. Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Start RabbitMQ
```bash
# Using Docker (recommended)
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:4-management

# Access RabbitMQ Management UI: http://localhost:15672
# Default credentials: guest / guest
```

### 6. Start the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will:
- Start FastAPI server on `http://localhost:8000`
- Automatically start email worker thread
- Begin listening for email tasks

## Project Structure

```
pay-link/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings configuration
│   │   ├── database.py        # Database setup
│   │   ├── enum.py            # Enums
│   │   ├── logger.py          # Centralized logging
│   │   ├── model.py           # Database models
│   │   └── schema.py          # Pydantic schemas
│   ├── middleware/
│   │   └── auth_middleware.py # Authentication middleware
│   ├── routes/
│   │   ├── auth.py            # Auth endpoints
│   │   └── user.py            # User endpoints
│   ├── services/
│   │   ├── auth.py            # Authentication service
│   │   ├── emails.py          # Email service (MailerSend)
│   │   └── queue.py           # RabbitMQ connection
│   ├── workers/
│   │   └── email.py           # Email queue producer & consumer
│   ├── templates/
│   │   └── verify-email.html  # Email templates
│   ├── utils/
│   │   └── user_utils.py      # Utility functions
│   ├── __init__.py
│   └── main.py                # FastAPI app entry point
├── logs/                      # Application logs
├── .env                       # Environment variables
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Logging

Logs are automatically configured based on the `ENVIRONMENT` variable:

- **dev**: DEBUG level (verbose)
- **prod**: WARNING level (quiet)
- **test**: INFO level (normal)

Logs are written to:
- Console: Real-time output
- File: `logs/paylink.log` (rotated at 10MB, keeps 5 backups)

## License

MIT

## Support

For issues and questions, please create an issue in the repository.

## NB:

This is an ongoing slow project. If you run it now, you have nothing but basic features available. 