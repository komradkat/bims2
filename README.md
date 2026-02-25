# BIMS2 - Barangay Information Management System

BIMS2 is a comprehensive information management system designed for local government units (Barangays). It streamlines administrative tasks, enhances data management, and provides advanced features like GIS mapping for resident and infrastructure tracking.

## Core Modules

- **Core**: System settings, dashboard, and authentication.
- **Residents**: Management of resident profiles, demographic data, and tracking.
- **Certificates**: Issuance and management of barangay clearances, residency permits, and other documents.
- **Blotter**: Recording and monitoring of incident reports and disputes.
- **Business**: Management of business permits and local economic data.
- **Finance**: Budget tracking, expenses, and revenue management.
- **GIS (Ultra Tier)**: Interactive map with GTA-style "blips" for residents and emergency services.
- **Audit**: Comprehensive logging of system actions for accountability.

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTMX, Alpine.js, Vanilla CSS
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Mapping**: Leaflet.js
- **Package Management**: [uv](https://github.com/astral-sh/uv)

---

## Environment Setup

This project uses environment variables for configuration.

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

### 3. Run Migrations

```bash
uv run python manage.py migrate
```

### 4. Create Superuser

```bash
uv run python manage.py createsuperuser
```

### 5. Run Development Server

```bash
uv run python manage.py runserver
```

### 6. Run with Docker (Alternative)

If you prefer using Docker, you can start the system with:

```bash
docker compose up --build
```

## Quick Start (PowerShell / Windows)

For a fresh install, everything (dependencies, environment, and database) can be set up automatically:

```powershell
./run.ps1 -Setup
```

This will:
1.  Verify `uv` is installed.
2.  Auto-create `.env` if missing.
3.  Install all Python dependencies (`uv sync`).
4.  Run all database migrations.
5.  Launch the development server on `http://localhost:8001`.

---

## Local Testing & Environments

BIMS2 supports multiple configuration profiles for local development and production simulation.

### 🟢 Development Environment (Default)
Uses standard `.env` settings and stores data in `C:\BIMS_Data`.
```powershell
./run.ps1 dev 8001
```

### 🔵 Production Simulation (Hardened Test)
Uses `.env.prod` and production security settings.
```powershell
./run.ps1 prod 9002
```

> [!TIP]
> **Protip**: Use port `9002` or `9003` for production tests to avoid "Sticky" HTTPS redirections your browser might have cached for port 8000/8001.

---

## License System

BIMS2 features a tiered license system to unlock specific modules.

### License Tiers

- **Community** (Free): Residents, Certificates, Blotter
- **Pro**: Community + Business Permits, Finance, Audit Logs
- **Ultra**: Pro + GIS Mapping (GTA-style Blips)

### Development Bypass

When `DEBUG=True` or `LICENSE_DEBUG_BYPASS=True` in `.env`, the system automatically grants **Ultra tier** access.

---

## GIS Features

The GIS module provides a visual interface for managing barangay assets:

- **Resident Locations**: View where residents live on an interactive map.
- **GTA-style Blips**: Dynamic icons for Emergency Services (Police, Fire, Hospitals).
- **Custom Points**: Add and manage "Blips" for landmarks, evacuation centers, and more.
- **Resident GeoJSON**: Real-time spatial data rendering.

---

## Project Structure

```text
bims2/
├── apps/               # Application modules
│   ├── core/           # Dashboard & Auth
│   ├── residents/      # Resident Records
│   ├── certificates/   # Document Issuance
│   ├── gis/            # GIS Mapping Engine
│   └── ...             # Other modules
├── config/             # Django Settings & URLs
├── templates/          # HTML Templates (Jinja2-style)
├── static/             # Static Assets (JS/CSS)
├── manage.py           # Django Management Tool
└── pyproject.toml      # Project Metadata & Deps
```

## Security Best Practices

- Change `SECRET_KEY` in production.
- Set `DEBUG=False` in production.
- Use strong database passwords and configure `ALLOWED_HOSTS` properly.
- **Never commit `.env` to version control.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

