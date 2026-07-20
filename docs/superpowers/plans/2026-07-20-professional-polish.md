# Shelter Professional Polish — Implementation Plan

> **For agentic workers:** Execute inline or with `execute-tasks`.  
> Track steps with checkbox (`- [ ]`) syntax.  
> **Do NOT deploy / push to production until the user reviews.**

**Goal:** Ship a portfolio-ready polish pass: favicon/OG, About, mobile nav, empty states, 500 page, richer seed, README+CI, security headers — all local-only until review.

**Architecture:** Keep single Django app `catalog` + `config`. Presentation changes in templates/static; About is a simple template view; health endpoint optional via view; CI is GitHub Actions running `manage.py test` with SQLite.

**Tech Stack:** Django 5.2, existing static CSS/JS, GitHub Actions, WhiteNoise.

## Global Constraints

- English UI copy for public site
- No deploy / no `git push` / no `vercel --prod` until user says so
- Local commits OK if useful; prefer one logical commit at end if user wants
- TDD for backend routes (about, health, 500 handler, security settings smoke)
- YAGNI: no SPA, no OAuth, no new product domains
- Windows PowerShell: chain with `;` not `&&`

## Package map (user-approved)

| # | Deliverable |
|---|-------------|
| 1 | Favicon + Open Graph + About page |
| 2 | Mobile nav (hamburger) |
| 3 | Empty states + 500 page |
| 4 | Stronger seed data |
| 5 | README polish + screenshot guide + CI tests |
| 6 | Production security headers |

## File Map

| Path | Responsibility |
|------|----------------|
| `static/img/favicon.svg` | Brand mark favicon |
| `static/img/og-default.svg` or `.png` | Default social share image |
| `templates/base.html` | Meta OG, favicon, mobile nav, footer links |
| `templates/catalog/about.html` | About / why this project |
| `templates/500.html` | Server error page |
| `templates/catalog/home.html` | Empty featured/recent polish |
| `templates/catalog/book_list.html` | Empty search polish |
| `templates/catalog/my_shelf.html` | Empty shelf polish |
| `static/css/site.css` | Nav mobile, empty, about, 500 styles |
| `static/js/site.js` | Mobile nav toggle |
| `catalog/views.py` | `about`, `health`, `server_error` |
| `catalog/urls.py` | `/about/`, `/health/` |
| `config/urls.py` | `handler500` |
| `config/settings.py` | Security headers when not DEBUG |
| `catalog/management/commands/seed_catalog.py` | More books/authors |
| `catalog/tests/test_views.py` | About, empty-ish, 500 |
| `catalog/tests/test_security.py` | Security headers / health |
| `catalog/tests/test_seed.py` | Seed count expectations |
| `README.md` | Architecture, live URL, screenshots section |
| `docs/screenshots/README.md` | How to capture 3 shots |
| `.github/workflows/ci.yml` | Run tests on PR/push |
| `.env.example` | Document security-related vars |

---

## Task 1: Favicon + OG meta + About page

**Files:**
- Create: `static/img/favicon.svg`, `static/img/og-default.svg`, `templates/catalog/about.html`
- Modify: `templates/base.html`, `catalog/views.py`, `catalog/urls.py`, `catalog/tests/test_views.py`

- [ ] **Step 1:** Failing tests for `GET /about/` → 200 + key copy; home still 200
- [ ] **Step 2:** Implement `about` view + URL + template
- [ ] **Step 3:** Add favicon + OG tags in `base.html` (blocks for title/description/image)
- [ ] **Step 4:** Footer + nav link to About
- [ ] **Step 5:** Tests green

---

## Task 2: Mobile nav

**Files:**
- Modify: `templates/base.html`, `static/css/site.css`, `static/js/site.js`

- [ ] **Step 1:** Markup: menu toggle button + collapsible `.nav`
- [ ] **Step 2:** CSS: hide toggle desktop; drawer/stack mobile; focus styles
- [ ] **Step 3:** JS: toggle `aria-expanded`, body class optional
- [ ] **Step 4:** Manual smoke: resize + keyboard Esc close

---

## Task 3: Empty states + 500 page

**Files:**
- Create: `templates/500.html`
- Modify: empty blocks in home/list/shelf, `catalog/views.py`, `config/urls.py`, CSS, tests

- [ ] **Step 1:** Test `handler500` / `server_error` view returns 500 + copy (with DEBUG=False)
- [ ] **Step 2:** Implement `server_error` + `handler500`
- [ ] **Step 3:** Richer empty markup (title, lede, CTA) + CSS `.empty-state`
- [ ] **Step 4:** Tests green

---

## Task 4: Stronger seed

**Files:**
- Modify: `seed_catalog.py`, `test_seed.py`

- [ ] **Step 1:** Expand authors (6+) and books (16–18) with covers
- [ ] **Step 2:** Update seed tests for minimum counts
- [ ] **Step 3:** Run seed locally + tests

---

## Task 5: README + screenshot guide + CI

**Files:**
- Create: `.github/workflows/ci.yml`, `docs/screenshots/README.md`
- Modify: `README.md`, `.env.example`

- [ ] **Step 1:** CI workflow: checkout, Python 3.12, pip install, `manage.py test` (SQLite)
- [ ] **Step 2:** README sections: architecture, features, live URL, how to run, tests, API, stack proof
- [ ] **Step 3:** Screenshot capture instructions (Home, Books search, Manage) — user captures later
- [ ] **Step 4:** `.env.example` complete

---

## Task 6: Production security headers

**Files:**
- Modify: `config/settings.py`
- Create: `catalog/tests/test_security.py`

- [ ] **Step 1:** When `not DEBUG`: `SECURE_SSL_REDIRECT` careful on Vercel (proxy), HSTS, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_REFERRER_POLICY`, CSRF/session already secure
- [ ] **Step 2:** `GET /health/` → `{"status":"ok"}`
- [ ] **Step 3:** Tests with `override_settings(DEBUG=False)` for headers where testable

**Note:** On Vercel, `SECURE_SSL_REDIRECT` can loop if mis-set; prefer HSTS + secure cookies + proxy SSL header (already present). Use `SECURE_SSL_REDIRECT = False` on Vercel or only when env set.

---

## Verification (local only)

```powershell
$env:DATABASE_URL = "sqlite:///$pwd/test_local.sqlite3"
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check --deploy  # may warn; OK
```

**Stop:** Present summary for user review. **Do not push / deploy.**
