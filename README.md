# BIMS2 - Barangay Information Management System

## Environment Setup

This project uses environment variables for configuration. Follow these steps to set up your development environment:

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database (SQLite by default)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# For PostgreSQL (optional):
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=bims2_db
# DATABASE_USER=postgres
# DATABASE_PASSWORD=your_password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1

# License Settings
LICENSE_DEBUG_BYPASS=True
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

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug mode | `True` | No |
| `SECRET_KEY` | Django secret key | Auto-generated | No |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` | No |
| `DATABASE_ENGINE` | Database backend | `django.db.backends.sqlite3` | No |
| `DATABASE_NAME` | Database name/path | `db.sqlite3` | No |
| `DATABASE_USER` | Database username | `` | No |
| `DATABASE_PASSWORD` | Database password | `` | No |
| `DATABASE_HOST` | Database host | `` | No |
| `DATABASE_PORT` | Database port | `` | No |
| `LICENSE_DEBUG_BYPASS` | Bypass license checks (grants Ultra tier) | `False` | No |

## License System

### Development Mode

When `DEBUG=True` or `LICENSE_DEBUG_BYPASS=True`, the system automatically grants **Ultra tier** access to all features without requiring license activation.

### Production Mode

Set `DEBUG=False` and `LICENSE_DEBUG_BYPASS=False` to enable full license verification:

1. Generate license keys:
```bash
uv run python manage.py generate_licenses --tier ultra --count 1 --days 365
```

2. Activate license at `/license/activate/`

### License Tiers

- **Community** (Free): Residents, Certificates, Blotter
- **Pro**: Community + Business Permits, Finance, Audit Logs
- **Ultra**: Pro + GIS Mapping

## Project Structure

```
bims2/
├── apps/
│   └── core/           # Core application
├── config/             # Django settings
├── templates/          # HTML templates
├── static/             # Static files
├── .env                # Environment variables (not in git)
├── .env.example        # Environment template
└── manage.py           # Django management
```

## Security Notes

- **Never commit `.env` to version control** (already in `.gitignore`)
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong database passwords
- Configure `ALLOWED_HOSTS` properly in production
