# Share Your Dish (Python)

Flask recipe-sharing application with category browsing, budget-friendly tags, accounts, recipe uploads, and a responsive editorial UI. An empty database is automatically populated with three starter recipes per category.

## Run locally

Python 3.12+ is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open http://127.0.0.1:5000. SQLite data and local uploads are stored in the ignored `instance/` folder. Set a long random `SECRET_KEY` before exposing the app.

## Vercel deployment

Deploy this project root to Vercel. `app.py` exports the Flask WSGI application as `app`, which Vercel detects as a Python function. For a complete deployment, add `SECRET_KEY` and `DATABASE_URL` in Vercel Project Settings → Environment Variables, apply them to Production (and Preview if used), then redeploy. `DATABASE_URL` must point to a managed PostgreSQL database for durable users and recipes; SQLite on Vercel is ephemeral. A new database starts with 21 budget-friendly recipes across all seven categories.

`DATABASE_URL` is optional: without it, the app uses embedded SQLite and account creation, login, recipe sharing, and local uploads still work. On Vercel this fallback is stored in `/tmp`, which is ephemeral and may be replaced between function instances, so new accounts, recipes, and photos are not guaranteed to persist. Set `DATABASE_URL` to managed PostgreSQL for durable records. Connect a **public** Vercel Blob store to persist uploaded photos and set `BLOB_STORE_ID`/OIDC credentials or `BLOB_READ_WRITE_TOKEN`; without Blob, image uploads use temporary local storage.

Set a stable, long random `SECRET_KEY` in Vercel project settings so users remain signed in across function instances. If it is omitted, the site still runs, but generated session keys may invalidate sessions when Vercel starts a different instance.

The included food photography uses remote Unsplash image URLs. User uploads must be JPEG, PNG, WebP, or GIF and are limited to 4 MiB to fit within Vercel's request-size limit.

## Import existing XAMPP data

To copy the current MySQL recipes and users into the Python app's local SQLite database, with XAMPP MySQL running:

```powershell
python migrate_mysql.py
```

The importer reads the existing `share-your-dish` database using local XAMPP defaults. Set `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` to override them. The import is repeatable and retains legacy password hashes.

For a deployed site, set `DATABASE_URL` to the production Postgres URL before running the importer locally. Connect the production public Blob store and load its environment variables first; the importer uploads the existing recipe photo to Blob when those credentials are available. Without Blob credentials, it stores the photo in `static/images/` for the local deployment bundle.
