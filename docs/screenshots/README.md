# Screenshots

Checked into this folder for the project README:

| File | Page |
|------|------|
| `01-home.png` | `/` |
| `02-books-search.png` | `/books/?q=grace` |
| `03-manage.png` | `/manage/` (staff login) |

## Recapture (optional)

```powershell
# Terminal 1
python manage.py runserver

# Terminal 2 — example with playwright-cli
playwright-cli open http://127.0.0.1:8000/
playwright-cli resize 1400 900
playwright-cli screenshot --filename docs/screenshots/01-home.png
```

For manage: log in as staff first, then screenshot `/manage/`.

Live site: https://shelter-phi.vercel.app
