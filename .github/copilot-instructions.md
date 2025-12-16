<!-- Copilot instructions for code contributors and AI coding agents -->
# Copilot / AI Agent Instructions — Django Inventory Management App

Summary
- Short: this repo is a Django-based inventory system (apps: `inventorymgmt`, `suppliers`, `accounts`). Key integrations: Supabase for optional image storage, Pillow for image processing, and FastAI mentioned in docs for ML categorization.

What to read first
- `README.md`: high-level features, install steps, and ML notes.
- `djangoproject/settings.py`: env-driven configuration (uses `python-dotenv`) and lists installed apps, cache, static/media settings, and Supabase keys.
- `inventorymgmt/supabase_storage.py`: Supabase REST API usage, upload/delete/get URL helpers and runtime tips about RLS and keys.
- `inventorymgmt/utils.py`: image compression helper used before uploads.

Quick dev workflow (verified in repo)
- Create venv and activate:
```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
```
- Install deps: `pip install -r requirements.txt`
- Set env vars (use a `.env` file). Important keys: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, DB_* (DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT), `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_BUCKET_NAME`.
- DB migrate & run server:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py runserver
```
- Run tests: `python manage.py test`

Project-specific conventions & gotchas
- Apps: the repo relies on `inventorymgmt`, `suppliers`, and `accounts` (see `INSTALLED_APPS`). If you add a new app, register it there.
- ML: README references an `mlpredict` app and FastAI models, but `mlpredict` is not present in `INSTALLED_APPS` in `djangoproject/settings.py`. Confirm whether the ML app exists before changing ML code.
- Supabase: image uploads use the REST endpoint in `inventorymgmt/supabase_storage.py` (not the official SDK). Uploads may fail with Row-Level Security (RLS) enabled — see printed tips in that module.
- Image handling: uploaded images are compressed via `inventorymgmt/utils.py` before upload and stored under `media/product_images/` locally. `Pillow` is required for these flows.
- Static config: `whitenoise` is configured; `STATIC_ROOT` is set to `static/img` — be careful when changing collectstatic paths.
- Settings are env-driven via `dotenv` — prefer adding secrets to a `.env` for local dev, and keep them out of source control.

Integration points to inspect when changing features
- `inventorymgmt/supabase_storage.py` — Supabase upload/delete behavior and public URL construction.
- `djangoproject/settings.py` — feature flags (DEBUG), DB engine defaults to Postgres via env, Supabase/whitenoise config, and static/media roots.
- Template layout: `templates/` contains `base/`, `inventory/`, `suppliers/`, `accounts/` — follow existing patterns for forms, pagination, and messages.

Code examples to copy when making changes
- Add env-backed setting in `djangoproject/settings.py`:
```py
MY_FLAG = os.getenv('MY_FLAG', 'False').lower() == 'true'
```
- Use the Supabase helper singleton:
```py
from inventorymgmt.supabase_storage import get_supabase_storage
storage = get_supabase_storage()
url = storage.upload_image(image_file, filename)
```

When in doubt
- Verify `INSTALLED_APPS` and `settings.py` before adding cross-cutting changes (auth, static/media, caching).
- Check `README.md` for developer commands; tests are run with Django's test runner.

Ask me (the repo maintainer) before
- Changing `STATIC_ROOT` or `MEDIA_ROOT` paths.
- Replacing Supabase upload behavior (RLS requirements, public vs private buckets).

If anything in these notes is unclear or missing, tell me which area to expand (ML, Supabase, or deployment steps).
# StockMate - AI Agent Instructions

## Project Overview

**StockMate** is a Django 5.2 inventory management system featuring real-time stock tracking, supplier management, cloud image storage via Supabase, and comprehensive audit trails. The app runs on PostgreSQL (Supabase) with Gunicorn + WhiteNoise for production deployment on Render.

## Architecture & Key Decisions

### Data Flow Architecture

1. **Stock Model** (core entity) → **Supabase Storage** (images as URLs)
2. **Stock → Sale** (1-to-many, SET_NULL for orphaned sales)
3. **Stock → StockHistory** (audit trail, automatically created on mutations)
4. **Stock → Supplier** (many-to-one with related_name='stocks')

**Critical Pattern**: Images stored as `URLField` (not `ImageField`) pointing to Supabase CDN. This decouples storage from database and enables cloud uploads.

### Multi-App Structure

- **inventorymgmt**: Core CRUD + transactions (issue/receive items)
- **suppliers**: Supplier/Brand management with prefetch_related optimization
- **accounts**: Auth (register/login/password reset via Django signals)

### Deployment Stack

- **Local Dev**: SQLite (or PostgreSQL with SSL) via `.env`
- **Render Production**: Gunicorn + WhiteNoise + PostgreSQL (Supabase)
- **Static Files**: WhiteNoise config in settings (compressed manifest storage)

## Critical Technical Patterns

### 1. Environment Variables (`.env` Loading)

```python
# settings.py pattern
from dotenv import load_dotenv
load_dotenv()
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',')]
```

**Important**: Strip whitespace after split() to avoid DNS/CORS errors. `.env` MUST be in `.gitignore`.

### 2. Supabase Image Upload Workflow

- **Form**: `StockCreateForm.image` is separate `FileField` (NOT in Meta.fields)
- **Upload**: `SupabaseStorage().upload_image(image_file, filename)` returns public URL
- **Storage**: URL stored in `Stock.image` (URLField, max_length=500)
- **Cleanup**: Django signal handlers (`pre_save`, `post_delete`) auto-delete old files from Supabase

**File**: `inventorymgmt/supabase_storage.py` uses REST API (not supabase client library due to compatibility).

### 3. Audit Trail via StockHistory

Every stock mutation (add/issue/receive) creates a `StockHistory` record:

```python
StockHistory.objects.create(
    stock_id=item.id,
    item_name=item.item_name,
    quantity=item.quantity,
    # ... copy all Stock fields
)
```

**Location**: Created in views (`add_items`, `issue_items`, `receive_items`) and signal handlers.

### 4. Pagination Ordering Requirement

**Pattern**: Always order QuerySet before pagination to avoid `UnorderedObjectListWarning`:

```python
queryset = Stock.objects.select_related('supplier').all().order_by('item_name')
paginator = Paginator(queryset, 10)
```

### 5. Sale Model Cascading Behavior

- **ForeignKey**: `stock = ForeignKey(Stock, on_delete=SET_NULL, null=True)`
- **Rationale**: Allow orphaned sales when stock deleted (preserves transaction history)
- **Delete Sale**: Must check `if sale.stock:` before accessing stock attributes

### 6. Form Patterns

- **Dynamic supplier_name field**: `StockCreateForm` accepts supplier name as text, looks up or creates Supplier
- **Image validation**: File size (max 5MB) + content_type check in `clean_image()`
- **Separate image field**: Image NOT in `Meta.fields`, handled in custom `save()` method

### 7. Template Image Display

- **Supabase URLs**: Use `{{ stock.image }}` directly (URLField returns public URL)
- **Loop variables**: Match variable names (`item` vs `instance`) carefully
- **Mobile responsive**: Use Bootstrap `d-none d-md-block` for hiding elements

## Database & Migrations

### Current Schema

- **Stock**: item_name, quantity, category, brand, price, reorder_level, image (URLField), supplier (FK)
- **StockHistory**: Mirrors Stock fields + stock_id (not FK to preserve history)
- **Sale**: quantity_sold, stock (FK SET_NULL), created_at, ...
- **Supplier**: name, contact, ...
- **Brand**: (from suppliers app)

### Migration Command

```bash
python manage.py makemigrations
python manage.py migrate
```

## Development Workflow

### Local Setup

```bash
# Activate venv
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

### Testing Database Connection

```bash
# For Supabase PostgreSQL
python manage.py dbshell
```

### Common Commands

```bash
python manage.py createsuperuser         # Create admin user
python manage.py dumpdata > backup.json  # Backup data
python manage.py loaddata backup.json    # Restore data
python manage.py test                    # Run tests
```

## Supabase Integration Specifics

### REST API Approach

- **Endpoint**: `{SUPABASE_URL}/storage/v1/object/{bucket}/{path}`
- **Auth Header**: `Authorization: Bearer {SERVICE_ROLE_KEY}`
- **Public URL Format**: `{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}`
- **Why REST API**: Avoids supabase client library version conflicts

### Configuration (`settings.py`)

```python
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # For uploads
SUPABASE_BUCKET_NAME = os.getenv('SUPABASE_BUCKET_NAME', 'inv_management')
```

## Render Deployment

### Key Files

- **Procfile**: `web: gunicorn djangoproject.wsgi:application --bind 0.0.0.0:$PORT`
- **render.yaml**: Environment variables, database connection pooling config
- **build.sh**: Custom build script (compiles static files with WhiteNoise)

### Static Files Strategy

- **WhiteNoise Middleware**: Added after SecurityMiddleware in `MIDDLEWARE`
- **Storage**: `CompressedManifestStaticFilesStorage`
- **Compression**: Gzip + Brotli compression for assets

### Environment Variables for Production

```
DEBUG=False
ALLOWED_HOSTS=deploy-inv-management.onrender.com,localhost
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Common Patterns & Anti-Patterns

### ✅ DO

- Use `select_related()` for ForeignKey queries (Stock ← Supplier)
- Add `.order_by()` to QuerySets before pagination
- Wrap Supabase imports in try/except (conditional imports for development)
- Check null relationships before accessing: `if sale.stock:`
- Create `StockHistory` records for audit trail
- Use Django messages framework for user feedback

### ❌ DON'T

- Store image files locally (use Supabase CDN instead)
- Use `ImageField` (use `URLField` with Supabase URLs)
- Forget to strip whitespace from `ALLOWED_HOSTS` split()
- Call `image.url` on URLField (it's a direct string URL)
- Use `ON_DELETE=PROTECT` for Sale.stock (prevents deletion)
- Paginate without ordering (causes warnings and unpredictable results)

## Testing Checklist

- [ ] Login/logout flow works
- [ ] Can add stock with image upload to Supabase
- [ ] Images display on all pages (list_items, stock_details, pos_page)
- [ ] Delete stock with sales doesn't crash (orphaned sales preserved)
- [ ] Pagination shows 10 items without warnings
- [ ] Supplier dropdown in forms works (create or select existing)
- [ ] Mobile view hides logo section (`d-none d-md-block`)
- [ ] StockHistory records created on transactions

## Key Files Reference

| File                                  | Purpose                                            |
| ------------------------------------- | -------------------------------------------------- |
| `inventorymgmt/models.py`             | Stock, StockHistory, Sale models + signal handlers |
| `inventorymgmt/forms.py`              | StockCreateForm with Supabase upload in save()     |
| `inventorymgmt/supabase_storage.py`   | REST API wrapper for uploads/deletes               |
| `inventorymgmt/views.py`              | CRUD views + StockHistory creation logic           |
| `djangoproject/settings.py`           | Env loading, Supabase config, WhiteNoise setup     |
| `templates/base/base.html`            | Navigation + responsive layout                     |
| `templates/inventory/list_items.html` | Stock list with pagination + image display         |

---

**Last Updated**: December 2025 | **Django Version**: 5.2.5 | **Status**: Production-ready on Render
