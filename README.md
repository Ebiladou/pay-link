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
- ⏱️ **Rate Limiting** - Redis-backed per-user rate limiting to prevent abuse

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

### Rate Limiting

The application includes per-user rate limiting powered by Redis:

- **Per-User Tracking** - Authenticated users are rate limited by user ID
- **Per-IP Fallback** - Unauthenticated requests are tracked by IP address
- **Configurable Limits** - Each route can have custom rate limits

**Default Rate Limits:**
- `/auth/login` - 5 requests per 60 seconds
- `/auth/signup` - 3 requests per 60 seconds

**Customizing Rate Limits:**

Edit `app/middleware/rate_limiter.py` and modify `DEFAULT_ROUTES`:

```python
DEFAULT_ROUTES = [
    RouteRateLimit(path="/auth/login", requests=5, seconds=60),
    RouteRateLimit(path="/auth/signup", requests=3, seconds=60),
]
```

Or pass custom routes in `app/main.py`:

```python
rate_limit_routes = [
    RouteRateLimit(path="/auth/login", requests=10, seconds=60),
]
app.add_middleware(RateLimiterMiddleware, routes=rate_limit_routes)
```

## Prerequisites

- Python 3.12+
- PostgreSQL
- RabbitMQ
- Redis
- pip/virtualenv

## Installation

### Step 0: Clone the Repository

```bash
git clone git@github.com:Ebiladou/pay-link.git
cd pay-link
```

### Recommended (Docker quick start)

Run the full development stack (web + Postgres + Redis + RabbitMQ) with `docker-compose`. This is the fastest, most reproducible way to get started.

1. Copy the example environment file and set secrets (do NOT commit your `.env`):

```bash
cp .env.example .env
# edit .env and set real secrets (POSTGRES_PASSWORD, SECRET_KEY, etc.)
```

2. Build and start the stack:

```bash
docker-compose up --build
```

3. Stop / remove containers:

```bash
docker-compose down
```

Alternative: build and run only the web image (useful for quick iteration):

```bash
docker build -t paylink-web .
docker run --rm -p 8000:8000 --env-file .env paylink-web
```
Important notes:
- Keep real secrets out of source control: use `.env` (already ignored) or a secrets manager for production.
- The provided `docker-compose.yml` reads variables from `.env` (see `DATABASE_URL`, `REDIS_URL`, etc.).
- For production, replace `--reload` development server and consider a process manager, TLS, and secret management.

### Manual setup (optional)

If you prefer to run services locally without Docker, follow these steps after cloning the repo.

1. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start RabbitMQ (if not using Docker)

```bash
# Install or run RabbitMQ locally; docker run is an option:
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:4-management
```

5. Start Redis (if not using Docker)

```bash
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

6. Start the Application
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
│   │   ├── auth_middleware.py # Authentication middleware
│   │   └── rate_limiter.py    # Rate limiting middleware
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

This is an ongoing slow project. If you run it now, you have nothing but basic features available. README powered by AI.