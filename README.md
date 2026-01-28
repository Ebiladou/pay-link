# PayLink

A modern FastAPI-based payment link application with asynchronous email processing via RabbitMQ.

## Features

- 🔐 **User Authentication** - Secure signup, login, and password reset
- 📧 **Async Email Queue** - RabbitMQ-based email processing (non-blocking)
- 🔄 **Background Workers** - Email sending in separate threads
- 📝 **Centralized Logging** - Environment-aware logging with file rotation
- 🗄️ **PostgreSQL Database** - Using SQLModel and AsyncPG for async database operations
- 🎯 **RESTful API** - Clean API endpoints for user management

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

**Benefits:**
- API responses are instant (no email delays)
- Emails are processed reliably in background
- Failed emails are requeued automatically
- Main application thread never blocked

## Prerequisites

- Python 3.12+
- PostgreSQL
- RabbitMQ
- pip/virtualenv

## Installation

### 1. Clone the Repository
```bash
git clone <git@github.com:Ebiladou/pay-link.git>
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