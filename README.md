# EA Mart

EA Mart is a complete Django e-commerce store with a premium responsive interface, a session-aware shopping cart, secure account flows, and transaction-safe Cash on Delivery checkout. The included catalogue command adds **24 realistic demo products across 6 categories**.

The footer on every customer-facing page includes the required credit: **Developed by Estiuk Arafat Arnob**.

## Project highlights

1. **Premium storefront** — responsive product grids, search, category and price filters, sorting, pagination, product galleries, polished states, and accessible interaction patterns.
2. **Persistent shopping cart** — guest carts use Django sessions; account carts use the database; guest selections merge safely after registration or login.
3. **Secure order processing** — login-gated checkout, server-calculated prices, row-locked stock validation, atomic order creation, inventory reduction, and order history.
4. **Store administration** — searchable product and order management, inline order items and product galleries, status filters, image uploads, and an idempotent demo-data command.

## Technology

- Python and Django
- Django templates, HTML5, CSS3, and vanilla JavaScript
- SQLite by default, with environment-based database settings ready for PostgreSQL
- Pillow for admin image uploads

## Local setup

### 1. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and replace the development secret:

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` using File Explorer or:

```powershell
Copy-Item .env.example .env
```

The default settings use SQLite. Do not use the sample development secret in production.

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Load the demo catalogue

```bash
python manage.py seed_store
```

The command is safe to run repeatedly: it updates the same 24 products instead of duplicating them. To deliberately replace the current catalogue, run `python manage.py seed_store --clear`.

Product photography uses remote Unsplash image URLs; the interface automatically shows the included EA Mart placeholder if an image cannot load. Administrators can upload local product, category, gallery, and profile images.

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

No administrator password is included or hard-coded. After creating the account, visit `/admin/`.

### 7. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

### 8. Run the automated tests

```bash
python manage.py test
```

The suite covers registration, login/cart merging, cart quantities, stock limits, checkout authorization, server-side totals, free delivery, atomic stock validation, and order ownership.

## Main routes

| Route | Purpose |
| --- | --- |
| `/` | Home and curated collections |
| `/shop/` | Searchable, filterable product catalogue |
| `/product/<slug>/` | Product details |
| `/cart/` | Shopping bag |
| `/checkout/` | Authenticated checkout |
| `/account/register/` | Registration |
| `/account/login/` | Login |
| `/account/profile/` | Profile and delivery details |
| `/account/orders/` | Order history |
| `/admin/` | Django administration |

## Order logic

- Cash on Delivery is the only active payment method; the card option in the interface is visibly disabled and demo-only.
- Delivery costs ৳120 below ৳3,000 and is complimentary at or above ৳3,000.
- Prices and totals are calculated from current database values on the server.
- Checkout locks product rows, verifies stock, creates the order and line-item snapshots, reduces inventory, and clears the cart inside one database transaction.
- Available statuses are Pending, Confirmed, Processing, Shipped, Delivered, and Cancelled.

## PostgreSQL migration

Install a PostgreSQL driver such as `psycopg`, create a database, and set the commented `DB_*` variables from `.env.example`. Django models and queries do not depend on SQLite-specific application code. Run migrations against the new database before loading catalogue data.

## Production notes

- Set `DJANGO_DEBUG=False`, use a strong `DJANGO_SECRET_KEY`, and configure `DJANGO_ALLOWED_HOSTS`.
- Serve static and media files with your web server or object-storage setup.
- Configure HTTPS and verify secure-cookie and HSTS settings for your deployment.
- Replace remote demo imagery with owned or properly licensed production assets.

## Structure

```text
EA_Mart/
├── config/                 # Django project settings and root URLs
├── shop/                   # Models, forms, views, admin, cart logic, tests
│   ├── management/commands/seed_store.py
│   └── migrations/
├── templates/              # Store, account, component, and error templates
├── static/                 # Premium CSS, vanilla JS, image fallback
├── media/                  # User-uploaded assets during development
├── manage.py
├── requirements.txt
└── .env.example
```
