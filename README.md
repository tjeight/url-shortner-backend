# URL Shortener Backend

A production-oriented URL Shortener Backend built with FastAPI, PostgreSQL, Redis, and JWT Authentication.

## Features

### Authentication

* User Signup
* User Login
* Forgot Password
* Reset Password
* OTP Verification
* JWT Authentication
* Refresh Token Management
* Session Management

### URL Management

* Create Short URLs
* Retrieve User URLs
* Delete URLs
* Refresh URL Expiry
* URL Expiration Handling
* Public URL Redirection

### Analytics

* User Analytics Dashboard
* Admin Analytics Dashboard
* Total URL Count
* Total Click Count
* Unique Visitor Tracking
* Last Click Activity
* Click History

### Performance

* Redis-Based Caching
* Cache Invalidation Strategy
* Pagination
* Optimized Database Indexing

### Administration

* Admin Authentication
* Platform Analytics
* User Monitoring

---

# Tech Stack

## Backend

* FastAPI
* SQLAlchemy 2.0
* Alembic

## Database

* PostgreSQL

## Cache

* Redis

## Authentication

* JWT
* OTP Verification

## Email Service

* Resend

## Development Tools

* UV
* Pre-Commit
* Bruno

---

# Project Structure

```text
src/
├── configs/
│   ├── pg.py
│   ├── redis.py
│   ├── resend.py
│   └── settings.py
│
├── dependencies/
│   └── pg.py
│
├── modules/
│   ├── auth/
│   │   ├── admin/
│   │   └── user/
│   │
│   ├── urls/
│   │   └── user/
│   │
│   └── analytics/
│       ├── admin/
│       └── users/
│
├── routes/
│   ├── admin.py
│   └── user.py
│
├── templates/
│   └── otp.py
│
└── utils/
    ├── auth.py
    ├── cache.py
    ├── email.py
    └── generators.py
```

### Folder Explanation

#### configs/

Contains application configuration including:

* PostgreSQL connection
* Redis connection
* Resend configuration
* Environment settings

#### dependencies/

Reusable dependency injection components.

#### modules/

Contains business logic organized by feature.

##### auth/

Handles:

* Signup
* Login
* OTP Verification
* Password Reset
* JWT Authentication

##### urls/

Handles:

* URL Creation
* URL Retrieval
* URL Deletion
* URL Expiry
* URL Redirection

##### analytics/

Handles:

* Click Tracking
* User Analytics
* Admin Analytics

#### routes/

Main API route registration.

#### templates/

Email templates used for OTP delivery.

#### utils/

Shared utility functions including:

* Authentication Helpers
* Redis Cache Helpers
* Email Utilities
* Random Generators

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/tjeight/url-shortner-backend.git

cd url-shortner-backend
```

## Install Dependencies

```bash
uv sync --dev
```

## Install Pre-Commit Hooks

```bash
uv run pre-commit install
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=

REDIS_HOST=
REDIS_PORT=

JWT_SECRET_KEY=
JWT_ALGORITHM=

RESEND_API_KEY=

BASE_URL=
```

Configure the values according to your local environment.

---

# Database Migration

Apply migrations:

```bash
uv run alembic upgrade head
```

Create new migration:

```bash
uv run alembic revision --autogenerate -m "message"
```

---

# Run Application

Development Mode:

```bash
uv run fastapi dev main.py
```

Application will be available at:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc Documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# Caching Strategy

## User URLs

```text
urls:{user_id}:{page}:{size}
```

Used for caching paginated user URL listings.

## Redirect URLs

```text
url:{short_code}
```

Used for caching URL redirection lookups.

---

# Analytics Flow

```text
User Clicks Short URL
        ↓
Redirect Endpoint
        ↓
Store Click Analytics
        ↓
Redirect To Original URL
```

Captured Analytics:

* IP Address
* User Agent
* Click Timestamp

---

# Future Improvements

* Docker Support
* Nginx Reverse Proxy
* AWS Deployment
* Click Geo Tracking
* Browser Analytics
* Rate Limiting
* Custom Domains
* QR Code Generation

---

# Author

Tejas

GitHub:
https://github.com/tjeight
