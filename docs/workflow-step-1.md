# STEP 1 — Project Foundation Workflow

## Objective
Set up a clean, professional project structure with Git, Python virtual environment, and base dependencies.

---

## 1. Create Project Root
- Create folder: `ecommerce-analytics`
- Open folder in VS Code (File → Open Folder)

Purpose:
> Establish a single root directory for the entire system.

---

## 2. Create Base Folder Structure
Create the following folders inside the root:

- backend/
- dashboard/
- docker/
- docs/
- data/
- tests/

Purpose:
> Separate concerns early (backend, frontend, infra, docs, tests).

---

## 3. Initialize Git

---
## Step 2

In this step, I set up the local infrastructure layer for the project using Docker Compose.

What I implemented

Configured PostgreSQL as the primary analytics database using an official Docker image

Configured Redis as an in-memory data store and future message broker for background jobs

Created a Docker Compose configuration to run both services together

Added persistent volumes so database data survives container restarts

Added health checks to ensure services are ready before dependent components start

Created environment configuration files:

.env for local secrets (excluded from Git)

.env.example to document required environment variables

How it works

Docker Compose reads variables from .env

Containers start in isolation but share a Docker network

PostgreSQL listens on port 5432, Redis on 6379

Health checks verify database and cache availability

Services can later be reused by Django, Celery, and the dashboard without changes

Why this step matters

Ensures reproducible development environments

Removes dependency on locally installed databases

Mirrors production-like infrastructure early

Enables easy onboarding: docker compose up -d

Prepares the system for ETL pipelines and async processing

Result

PostgreSQL and Redis running reliably in containers

Verified connectivity to both services

Infrastructure ready for Django backend integration


---
## Step 3
Initialized a Django project inside backend/

Configured Django to read environment variables safely

Connected Django to the Postgres container using DATABASE_URL

Ran initial migrations to create core tables

Verified everything works by running the server and admin panel

---
## Step 4

 analytics app created

 analytics added to INSTALLED_APPS

 Models created: DimCustomer, DimProduct, DimTime, FactOrder

 makemigrations succeeded

 migrate succeeded

 Tables exist in Postgres (\dt shows them)

 (Optional) Models visible in Django Admin

 Committed to Git

---
## Step 5
 Faker installed + added to requirements

 python manage.py seed ... runs successfully

 Counts show data in all 4 tables

 (Optional) Data visible in admin

 Seed command committed

---
## Step 6
 analytics/queries.py created (SQL lives there)

 analytics/views.py has KPIView

 analytics/urls.py created

 config/urls.py includes api/v1/

 Endpoint returns JSON at /api/v1/kpis/

 Date filtering works + validates format

 (Optional) python manage.py test passes


---
## Step 7

fetch_revenue_trends() added to queries.py

 RevenueTrendsView added to views.py

 URL added: /api/v1/revenue/trends/

 Works for daily, weekly, monthly

 Returns JSON with points[]

---
## Step 8

fetch_rfm_segments() added in queries.py

 CustomerSegmentsView added to views.py

 URL works: /api/v1/customers/segments/

 Returns segments list + counts

 (Optional) tests pass


 ---
## Step 9

fetch_top_products() added in queries.py

 TopProductsView added in views.py

 URL works: /api/v1/products/top-sellers/

 Supports metric=revenue|quantity

 Supports limit (clamped to max 100)

 Returns ranked items[]

  ---
## Step 10
 Installed django-redis

 Added DJANGO_REDIS_URL to backend/.env

 Added CACHES config in settings.py

 Added caching logic to 4 endpoints

 Verified cache.hit becomes true on second request


  ---
## Step 11
 drf-spectacular installed + added to requirements

 drf_spectacular in INSTALLED_APPS

 REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] set

 SPECTACULAR_SETTINGS added

 /api/docs/ works

 /api/schema/ returns JSON

  ---
## Step 12
serializers.py created

 Orders list view added with pagination

 /api/v1/orders/ works

 Pagination fields appear (count, next, results)

 Filtering by customer_id works

   ---
## Step 13
 Installed djangorestframework-simplejwt

 DEFAULT_AUTHENTICATION_CLASSES set to JWTAuthentication

 Added /api/v1/auth/token/ and /api/v1/auth/token/refresh/

 Protected /api/v1/orders/ with IsAuthenticated

 Verified:

 /api/v1/orders/ returns 401 without token

 Works with Authorization: Bearer <access>

   ---
## Step 14
 etl app created

 etl added to INSTALLED_APPS

 ETLRun model created

 migrations applied successfully

 etl_runs table exists in Postgres

 model visible in Django Admin (optional)


   ---
## Step 15

data/raw/orders.csv created

 Pandas installed + added to requirements

 load_csv_orders management command created

 ETL run loads 10 orders on first run

 Second run loads 0 orders (idempotent)

 etl_runs shows success records


   ---
## Step 16
 Installed celery

 Added broker/backend env vars to backend/.env

 Created config/celery.py and wired it via config/__init__.py

 Added Celery settings + timezone

 Moved ETL logic into etl/jobs/load_csv_orders_job.py

 Management command calls the shared job

 Created Celery task etl/tasks.py

 Added CELERY_BEAT_SCHEDULE (every 5 minutes)

 Worker runs + Beat runs

 etl_runs shows scheduled runs

 ## Step 17
 ETLRunSerializer created

 ETL status endpoint works: /api/v1/etl/status/

 ETL trigger endpoint exists: /api/v1/etl/trigger/

 Trigger requires JWT (401 without token)

 Trigger returns 202 + task_id

 New ETLRun appears after trigger

 Swagger shows ETL endpoints

    ---
## Step 18
 Installed: dash, plotly, requests, pandas

 dashboard/app.py created

 Dashboard runs at http://127.0.0.1:8050

 KPI cards show values (not errors)

 Revenue trend chart loads

 Top products chart loads

     ---
## Step 19
dashboard/utils.py created (API helper)

 Navbar added

 Overview moved to pages/overview.py

 Customers page added with RFM pie

 Router added in dashboard/app.py

 Both routes work: / and /customers

      ---
## Step 20
dashboard/utils.py supports auth header

 Overview page has JWT token input

 Overview displays Recent Orders table

 Without token: shows helpful message (no crash)

 With token: orders load successfully

 ---
## Step 21
 docker/Dockerfile.dashboard runs python -m dashboard.app

 dashboard/__init__.py exists

 Dash binds 0.0.0.0

 docker ps shows ecommerce_dashboard

 Browser opens http://127.0.0.1:8050/

  ---
## Step 22

nstalled black, flake8, pytest, pytest-django

 pytest.ini created

 .flake8 created

 pyproject.toml created

 .github/workflows/ci.yml created

 Local checks pass

 GitHub Actions CI passes

 ## Step 23