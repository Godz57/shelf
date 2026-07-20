# Shelf — Design Spec (approved direction)

**Date:** 2026-07-19  
**Purpose:** Portfolio Django project for Crossway Web Developer (Django) candidacy.  
**Not a clone** of crossway.org — same *patterns* (catalog, admin, search, auth, thin API).

## Problem

Show verifiable Django skill: models, admin, templates, forms, auth, SQL/Postgres, a small JSON API, Git hygiene, and deploy — without claiming multi-year production Django tenure.

## Product one-liner

**Shelf** is a small gospel/Christian publishing catalog: browse books by author/category, search, view detail pages, sign up and keep a private reading list, plus staff tooling via Django Admin and a public read-only API.

## Personas

| Persona | Needs |
|---------|--------|
| Visitor | Browse, search, open book detail |
| Reader (auth) | Save books to “My Shelf” (wishlist / to-read) |
| Staff (superuser) | CRUD books/authors/categories via Admin |

## Scope — MVP (in)

1. Catalog models: Author, Category, Book (+ M2M authors, FK category)
2. Public list + detail pages (slug URLs), pagination
3. Search (title/subtitle/description) + filter by category + sort
4. Django Admin with search, filters, inlines
5. Auth: signup, login, logout
6. Reading list (My Shelf): add/remove book for logged-in user
7. Read-only JSON API: list + detail books
8. Seed command with fictional sample data
9. Tests (models, views, API, auth list)
10. Production-ready settings pattern (env vars, Postgres option)
11. README in English + deploy to Render/Railway

## Scope — out (YAGNI)

- Payments / cart / inventory
- Real Crossway/ESV content or branding
- SPA frontend / React
- Comments, ratings, recommendations ML
- Multi-tenant church accounts
- Full text search engines (Postgres `icontains` is enough)
- Email verification / OAuth (unless time left after MVP)

## Domain model (logical)

```
Author     id, name, slug, bio, created_at
Category   id, name, slug
Book       id, title, slug, subtitle, description, isbn,
           published_date, cover_url, is_featured, created_at,
           category (FK), authors (M2M)
ReadingListItem  user (FK), book (FK), notes, created_at  UNIQUE(user, book)
```

## Pages / endpoints

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/` | public | Home: featured + recent |
| GET | `/books/` | public | List + search/filter/sort |
| GET | `/books/<slug>/` | public | Detail |
| GET | `/authors/<slug>/` | public | Author detail + books |
| GET/POST | `/accounts/signup/` | guest | Create account |
| GET/POST | `/accounts/login/` | guest | Login |
| POST | `/accounts/logout/` | user | Logout |
| GET | `/my-shelf/` | user | Reading list |
| POST | `/my-shelf/add/<book_id>/` | user | Add |
| POST | `/my-shelf/remove/<book_id>/` | user | Remove |
| GET | `/api/books/` | public | JSON list (paginated) |
| GET | `/api/books/<slug>/` | public | JSON detail |
| * | `/admin/` | staff | Django Admin |

## UI principles

- Clean, readable, ministry-appropriate (not flashy startup purple)
- Server-rendered Django templates + small vanilla JS only if needed
- Mobile-friendly CSS (one base stylesheet; no heavy framework required — optional pico.css or simple custom CSS)
- English UI strings (US role / Crossway)

## Technical decisions

| Choice | Decision |
|--------|----------|
| Python | 3.12+ |
| Django | 5.x LTS-capable release |
| DB local | SQLite for dev |
| DB prod | PostgreSQL |
| API | Django REST Framework (minimal serializers/viewsets or APIViews) |
| Auth | Django built-in `User` + auth views/forms |
| Tests | `django.test.TestCase` + client |
| Deploy | Render or Railway free tier |
| Secrets | `python-dotenv` + env vars; never commit secrets |
| Project layout | single Django project `config`, apps: `catalog`, `accounts` (or `shelf` for reading list inside catalog) |

## App layout

```
shelf/                 # repo root
  config/              # settings, urls, wsgi
  catalog/             # books, authors, categories, reading list, API
  templates/           # base + app templates
  static/              # css, maybe js
  manage.py
  requirements.txt
  README.md
  .env.example
  Procfile or render.yaml
```

## Success criteria (portfolio / interview)

- [ ] `python manage.py test` green
- [ ] Live URL with seed data
- [ ] Admin usable for content
- [ ] README explains architecture and how to run
- [ ] GitHub repo public, clean history
- [ ] CV line becomes true: “Django catalog app with admin, auth, search, and JSON API, deployed with Postgres”

## Legal / brand

- Fictional books only; no Crossway trademarks, ESV text, or scraped product images.
- Optional one-line mission note in README: personal faith alignment for nonprofit ministry work — not product copy.
