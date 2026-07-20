# Shelf

A small **gospel-publishing catalog** built with **Django** for portfolio use.

Shelf demonstrates the same web patterns used by content/publishing products: catalog models, staff admin, search and filters, authenticated reading lists, and a thin read-only JSON API — server-rendered with Django templates (no SPA).

> **Disclaimer:** Fictional titles and authors only. **Not affiliated with Crossway** or any publisher. Built as a learning / portfolio project for a Web Developer (Django) candidacy.

## Features

- Book catalog with authors, categories, featured flags
- Public home, book list, book detail, author detail
- Search (title / subtitle / description / author), category filter, sort
- Django Admin with search, filters, and M2M widgets
- Sign up / log in / log out
- **My Shelf** personal reading list (add / remove)
- Read-only JSON API: `GET /api/books/`, `GET /api/books/<slug>/`
- Seed command with sample data
- Postgres-ready settings, WhiteNoise static files, Gunicorn `Procfile`
- Automated tests (`python manage.py test`)

## Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Framework | Django 5.2 |
| API | Django REST Framework |
| DB (dev) | SQLite |
| DB (prod) | PostgreSQL via `DATABASE_URL` |
| Static | WhiteNoise |
| Server | Gunicorn |

## Local setup

```powershell
cd shelf
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_catalog
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Tests

```powershell
python manage.py test
```

## API examples

```bash
curl http://127.0.0.1:8000/api/books/
curl http://127.0.0.1:8000/api/books/grace-and-truth/
```

## Project layout

```
config/          # settings, root URLs, WSGI
catalog/         # models, views, admin, API, seed command, tests
templates/       # base + catalog + registration templates
static/css/      # site styles
```

## Deploy (Render / Railway)

1. Push this repo to GitHub.
2. Create a web service + PostgreSQL database.
3. Set environment variables:

| Variable | Example |
|----------|---------|
| `DJANGO_SECRET_KEY` | long random string |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_ALLOWED_HOSTS` | `your-app.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` |
| `DATABASE_URL` | from the provider |

4. Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

5. Release / start:

```bash
python manage.py migrate && python manage.py seed_catalog
gunicorn config.wsgi --log-file -
```

(Or use the included `Procfile` for the web process.)

6. Create a superuser with a one-off shell: `python manage.py createsuperuser`

## Why this project

Crossway-style products are content-heavy web apps: catalogs, admin tooling, accounts, and APIs. Shelf is a focused exercise in those Django fundamentals — honest portfolio evidence, not a claim of years of production Django tenure.

## License

MIT — use and adapt freely for your own portfolio.
