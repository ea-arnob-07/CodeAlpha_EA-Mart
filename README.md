# 🛒 EA Mart

**EA Mart** is a complete, feature-rich Django e-commerce store with a premium responsive interface, a session-aware shopping cart, secure account flows, and transaction-safe Cash on Delivery checkout. 

This project is built for scale, featuring modern technologies like **PostgreSQL**, **Cloudinary** for image hosting, **Docker** for containerization, and a fully **custom Admin Panel** tailored for store management. 

---

## ✨ Project Highlights

1. **Premium Storefront** — Highly responsive product grids, search, category and price filters, sorting, pagination, product galleries, polished states, and accessible interaction patterns.
2. **Persistent Shopping Cart** — Guest carts use Django sessions; account carts use the database. Guest selections merge safely after registration or login.
3. **Secure Order Processing** — Login-gated checkout, server-calculated prices, row-locked stock validation, atomic order creation, inventory reduction, and order history.
4. **Custom Store Administration** — A dedicated, enhanced admin panel with searchable product and order management, inline order items and product galleries, status filters, and image uploads.
5. **Modern Tech Stack** — Fully containerized with **Docker**, using **PostgreSQL** as the primary database, and **Cloudinary** for scalable, cloud-based media management.
6. **Cloud Deployment Ready** — Fully configured for seamless deployment on **Vercel**.

---

## 🛠️ Technology Stack

- **Backend:** Python, Django
- **Frontend:** Django templates, HTML5, CSS3, Vanilla JavaScript
- **Database:** PostgreSQL (with SQLite fallback for local development)
- **Media Storage:** Cloudinary
- **Containerization:** Docker
- **Deployment:** Vercel (`vercel.json` included)
- **Image Processing:** Pillow

---

## 🚀 Quick Start (Local Setup)

### 1. Using Docker (Recommended)
If you have Docker installed, you can spin up the entire environment (including PostgreSQL) with a single command:
```bash
docker-compose up --build
```

### 2. Manual Setup
If you prefer running it without Docker:

**Create a virtual environment:**
```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure environment variables:**
Copy the example file and fill in your secrets (including Cloudinary and PostgreSQL credentials):
```bash
cp .env.example .env
```

**Apply migrations and seed data:**
```bash
python manage.py migrate
python manage.py seed_store  # Loads 24 realistic demo products
```

**Create an administrator:**
```bash
python manage.py createsuperuser
```

**Start the development server:**
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## ☁️ Deployment (Vercel)

This project includes a `vercel.json` file for easy deployment on Vercel.

1. Push your repository to GitHub.
2. Import the project in Vercel.
3. Add the required Environment Variables in Vercel settings (e.g., `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, Database credentials, and Cloudinary keys).
4. Deploy!

---

## 🗂️ Main Routes

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
| `/admin/` | Custom Django administration panel |

---

## ⚙️ Order & Business Logic

- **Payment:** Cash on Delivery is the active payment method. The card option in the UI is disabled for demo purposes.
- **Delivery:** Delivery costs ৳120 for orders below ৳3,000, and is free for orders at or above ৳3,000.
- **Security:** Prices and totals are calculated securely on the server. Checkout locks product rows, verifies stock, creates the order, reduces inventory, and clears the cart inside a single atomic database transaction.
- **Order Tracking:** Available statuses include Pending, Confirmed, Processing, Shipped, Delivered, and Cancelled.

---

## 👨‍💻 Developed By
**Estiuk Arafat Arnob**
