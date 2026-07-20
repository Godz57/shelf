# Shelter Portfolio Closeout — Implementation Plan

> Execute inline. **Commit + push** after meaningful milestones unless blocked.

**Goal:** Close the portfolio loop: screenshots in README, production health check + seed, staff cover URL preview, then stop for applications.

## Steps (order fixed)

| # | Deliverable |
|---|-------------|
| 1 | Capture 3 screenshots + wire into README |
| 2 | Verify production (live URL, seed content, mobile-ish) |
| 3 | Staff cover URL live preview on book form |
| 4 | Wrap-up checklist for applications (no more features) |

## File map

| Path | Responsibility |
|------|----------------|
| `docs/screenshots/01-home.png` | Home hero + featured |
| `docs/screenshots/02-books-search.png` | Books + search |
| `docs/screenshots/03-manage.png` | Staff manage (or dashboard fallback) |
| `docs/screenshots/README.md` | Update capture notes |
| `README.md` | Embed screenshots |
| `templates/staff/book_form.html` | Cover preview UI |
| `static/js/site.js` or staff-only JS | Preview on URL input |
| `catalog/tests/test_staff.py` | Form still works / preview markup |
| `static/css/site.css` | Preview styles |

## Task 1: Screenshots + README

- [ ] Capture via local runserver or live URL (Playwright/CLI if available)
- [ ] Save under `docs/screenshots/`
- [ ] Embed in README with captions
- [ ] Commit

## Task 2: Production check

- [ ] `GET` live home, about, health, api/books
- [ ] Confirm books/covers present (seed)
- [ ] If empty catalog, trigger seed path (build.py / note for user)
- [ ] Note mobile: responsive CSS already shipped; spot-check headers

## Task 3: Cover URL preview (staff)

- [ ] Book form: preview box next to `cover_url`
- [ ] JS: on input/change/paste, set `img.src` if URL looks like http(s)
- [ ] CSS: aspect ratio cover, broken-state message
- [ ] Test: staff book form page contains preview element

## Task 4: Application wrap

- [ ] Short checklist in README or response to user (CV line, links)
- [ ] No further features unless asked

## Constraints

- Same fonts/design language
- YAGNI: no upload backend unless already present
- Windows PowerShell
