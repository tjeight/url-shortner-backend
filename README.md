<div align="center">

# ⚡ URL Shortener Backend

**A production-grade URL shortening service — built to scale, secured to trust, deployed to the cloud.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/ec2/)
[![CI](https://img.shields.io/badge/GitHub_Actions-CI-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Overview

A fully-featured URL Shortener backend engineered with **FastAPI**, deployed on **AWS EC2**, and backed by **PostgreSQL** and **Redis**. From JWT-based auth with HttpOnly cookies to role-based analytics and automatic URL expiration — every layer is production-ready.

---

## 🏗️ Architecture

```
                ┌──────────────┐
                │    Client    │
                └──────┬───────┘
                       │ HTTPS
                       ▼
                ┌──────────────┐
                │    Nginx     │  ← Reverse Proxy
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   FastAPI    │  ← Application Layer
                └──────┬───────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 ┌──────────────┐             ┌──────────────┐
 │    Redis     │             │  PostgreSQL  │
 │    Cache     │             │   Database   │
 └──────────────┘             └──────────────┘
```

---

## 🚀 Features

### 🔐 Authentication
| Feature | Details |
|---|---|
| JWT Auth | Access Token + Refresh Token |
| Cookie Security | HttpOnly Cookies — XSS-safe |
| OTP Password Reset | Time-limited OTP via Resend Email |
| Signup / Login / Logout | Full auth lifecycle |

### 🔗 URL Management
- Create short URLs with automatic expiry
- View, delete, and refresh your URLs
- Lightning-fast redirects via Redis cache
- Paginated URL listings

### 📊 Analytics

**User-Level**
- Total URLs created
- Total clicks & unique visitors
- Click timestamps & history

**Admin-Level**
- Platform-wide usage insights
- Total users, URLs, and clicks
- Cross-user analytics

### ⚙️ DevOps
- Fully Dockerized with Docker Compose
- Nginx as reverse proxy
- AWS EC2 deployment
- GitHub Actions CI pipeline (lint, format, Docker build)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Pydantic |
| ORM | SQLAlchemy + Alembic |
| Database | PostgreSQL |
| Cache | Redis |
| Auth | JWT + HttpOnly Cookies |
| Email | Resend |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| Cloud | AWS EC2 |
| CI | GitHub Actions |

---

## 📂 Project Structure

```
src/
├── configs/            # App & DB configuration
├── dependencies/       # FastAPI dependency injection
├── modules/
│   ├── auth/
│   │   ├── admin/      # Admin auth routes
│   │   └── user/       # User auth routes
│   ├── urls/
│   │   └── user/       # URL management
│   └── analytics/
│       ├── admin/      # Admin analytics
│       └── users/      # User analytics
├── routes/             # Route registration
├── templates/          # Email templates
├── scripts/            # Utility scripts
└── utils/              # Helpers & shared logic
```

---

## 📸 Screenshots

### 🌐 Live Deployment on AWS EC2

The application is live and accessible on an AWS EC2 instance behind Nginx.

![Root Route after Deployment](docs/screenshots/root_route_after_deployement.png)

---

### 📋 All API Routes (Swagger UI)

Every endpoint is documented and explorable via FastAPI's built-in Swagger interface.

![All Routes](docs/screenshots/all_routes.png)

---

### 🔗 URL Redirect in Action

Short URLs resolve and redirect users correctly — cached via Redis for near-instant response.

![Redirect URL](docs/screenshots/redirect_url.png)

---

### 👤 User Registration on Live Server

Signup works end-to-end on the deployed EC2 instance — JWT tokens issued, cookies set.

![User Registration after Deployment](docs/screenshots/user_registration_after_deployment.png)

---

### ☁️ AWS EC2 Deployment

The full stack running on EC2 with Docker Compose, PostgreSQL, Redis, and Nginx.

![AWS Deployment](docs/screenshots/aws_deployment.png)

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=5432
POSTGRES_DB=

# JWT
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Resend (Email)
RESEND_API_KEY=
RESEND_EMAIL_DOMAIN=
RESEND_FROM_EMAIL=

# App
APP_NAME=URL Shortener
PASSWORD_RESET_OTP_EXPIRE_MINUTES=5
BASE_URL=
```

---

## 🧑‍💻 Local Development Setup

```bash
# 1. Clone the repo
git clone https://github.com/tjeight/url-shortner-backend.git
cd url-shortner-backend

# 2. Install dependencies (using uv)
uv sync --dev

# 3. Set up pre-commit hooks
uv run pre-commit install

# 4. Run database migrations
uv run alembic upgrade head

# 5. Start the dev server
uv run fastapi dev main.py
```

Swagger UI available at: `http://localhost:8000/docs`

---

## 🐳 Docker Setup

```bash
# Build and start all services
docker compose up -d --build

# Stop all services
docker compose down

# Tail logs
docker compose logs -f
```

---

## ☁️ AWS EC2 Deployment

The application runs on EC2 using Docker Compose with all services containerized:

```
GitHub Push
    │
    ▼
GitHub Actions CI (lint + build check)
    │
    ▼
AWS EC2 Instance
    │
    ▼
Docker Compose
    ├── FastAPI (App)
    ├── PostgreSQL (Database)
    ├── Redis (Cache)
    └── Nginx (Reverse Proxy)
```

---

## 🔄 GitHub Actions CI

Automated checks run on every push:

| Check | Tool |
|---|---|
| Dependency installation | `uv` |
| Linting | `ruff` |
| Format check | `ruff format` |
| Docker build validation | `docker compose build` |

Workflow: `.github/workflows/ci.yml`

---

## 📈 Roadmap

- [ ] Custom short URL slugs
- [ ] QR Code generation
- [ ] HTTPS via Let's Encrypt
- [ ] Rate limiting
- [ ] Automated test suite
- [ ] CD pipeline via GitHub Actions
- [ ] Click analytics dashboard
- [ ] Geographic analytics

---

## 👨‍💻 Author

**Tejas** — Backend Developer

Focused on FastAPI · PostgreSQL · Redis · System Design · Cloud Deployment · AI Engineering

> *Built with care for performance, security, and clean architecture.*

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).