# Chai Shots – Admin CMS + Public Catalog API

This project is a mini Content Management System (CMS) with a Public Catalog API and a background worker for scheduled publishing.  
It allows internal teams to manage Programs → Terms → Lessons, schedule lesson releases, and expose published content to consumers.

---

##  Architecture Overview

The system consists of three main services:

User → Web UI (Flask) → API → PostgreSQL
Worker (cron-like service)

### Services

- Web / API (Flask)
  - Admin CMS UI
  - Public Catalog API (published-only)
- Worker (Python)
  - Auto-publishes scheduled lessons
- Database
  - PostgreSQL
- Deployment
  - Railway (HTTPS)

---

##  Deployed URLs

- CMS Web App:  
  https://cms-assignment-production.up.railway.app  

- Public API Base:  
  https://cms-assignment-production.up.railway.app  

- Health Check:  
  https://cms-assignment-production.up.railway.app/health  

---

## Core Features

- Role-based CMS: **Admin / Editor / Viewer
- Manage:
  - Programs
  - Terms
  - Lessons
- Multi-language lesson content
- Asset validation:
  - Program posters (portrait + landscape)
  - Lesson thumbnails (portrait + landscape)
- Publishing workflow:
  - Draft
  - Scheduled
  - Published
  - Archived
- Background worker auto-publishes scheduled lessons
- Public Catalog API returns **published-only** data

---

## 🛠 Local Setup

### Prerequisites
- Docker
- Docker Compose

### Run Locally

docker compose up --build
This will start:

API / Web server

Worker

PostgreSQL database

Access:

CMS UI: http://localhost:5000

Health: http://localhost:5000/health

Database & Constraints
PostgreSQL used as managed database

SQLAlchemy models enforce:

Unique (program_id, term_number)

Unique (term_id, lesson_number)

Asset uniqueness per language + variant

Required language inclusion

Status-based publishing rules

Indexes added on:

Lesson (status, publish_at)

Program (status, language_primary, published_at)

🌱 Seed Data
The system supports seed data with:

At least 2 Programs

Multiple Terms

Multiple Lessons

Multi-language lessons

Posters and thumbnails

One scheduled lesson for demo auto-publish

⏰ Publishing Workflow
Lesson States
draft

scheduled

published

archived

Worker Logic
Runs every 30 seconds:

Finds lessons where:

status = 'scheduled'

publish_at <= now()

Publishes them:

status = 'published'

published_at = now()

Automatically publishes the parent Program if:

Program has ≥ 1 published lesson

✔ Idempotent
✔ Safe for repeated execution

🖥 CMS Web UI
Screens
Login

Dashboard

Manage Programs

Program Detail

Terms

Lessons

Posters

Lesson Detail

Thumbnails

Schedule / Publish

Public Catalog View

Roles
Role	Permissions
Admin	Full access
Editor	Create, edit, schedule, publish
Viewer	Read-only

All routes are protected at backend level (not just UI).

📡 Public Catalog API
Endpoints
List Programs GET /catalog/programs
Program Details GET /catalog/programs/<program_id>
Lesson Details GET /catalog/lessons/<lesson_id>
Behavior
Only published lessons are visible

Programs appear only if they contain ≥ 1 published lesson

Assets returned in structured format:

Program Assets

"assets": {
  "posters": {
    "en": {
      "portrait": "url1",
      "landscape": "url2"
    }
  }
}

Lesson Assets

"assets": {
  "thumbnails": {
    "en": {
      "portrait": "url1",
      "landscape": "url2"
    }
  }
}
🎯 Demo Flow (As Required)
Login as Editor / Admin

Create:

Program

Term

Lesson

Set Lesson:

status = scheduled

publish_at = now + 2 minutes

Wait for worker to run

Verify:

Lesson becomes published

Program auto-publishes

Open:

/catalog-ui
→ Lesson appears in public catalog

🧰 Tech Stack
Backend: Flask, SQLAlchemy

Database: PostgreSQL

Worker: Python background service

Containerization: Docker, Docker Compose

Deployment: Railway

📦 Local Run Requirement

docker compose up --build
Runs:

web/api

worker

db

🔒 Environment Variables
DATABASE_URL – PostgreSQL connection string

Secrets are not hard-coded

👩‍💻 Author
Amulya Angirekula
B.Tech (CSE)
Take Home Assignment – Chai Shots