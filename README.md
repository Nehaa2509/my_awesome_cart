# OQIREL

A full-stack Django e-commerce platform for a curated self-care & home-fragrance boutique — soy candles, reed diffusers, skincare, and apothecary goods. Built with real payment processing, authenticated user accounts, a wishlist, order tracking with PDF invoicing, and a blog with nested comments.

**Live demo:** https://oqirel-project.onrender.com

---

## Features

**Storefront**
- Category-organized product catalog (Fragrance, Skincare, Apothecary) with dynamic slideshows
- Product detail pages with view-count tracking and category-based recommendations
- Debounced AJAX search with live autocomplete suggestions
- Slide-out cart drawer with persistent `localStorage` state and a free-shipping progress indicator

**Accounts & Wishlist**
- Full authentication (signup, login, logout) via Django's session-based auth
- Personal wishlist — add/remove products, prevented from duplicate entries at the database level

**Checkout & Payments**
- Razorpay integration: order creation, hosted checkout, and server-side payment signature verification
- Authoritative server-side pricing and stock validation — client-submitted cart prices are never trusted; both are recalculated from the database at checkout
- Atomic stock decrement using SQL `F()` expressions to prevent overselling under concurrent checkouts

**Orders & Invoicing**
- Order status tracking by Order ID + email (for guests and registered users alike)
- Timestamped order-update timeline per order
- PDF invoice generation (ReportLab), gated behind login with an ownership check (matches the order to the requesting user via linked account or verified email, with staff override) so invoices can't be accessed by guessing order IDs

**Blog**
- Posts with categories, thumbnails, and author attribution
- Threaded/nested comments (self-referential parent field) and per-user post likes

**Admin**
- Custom-themed Django admin (branded header, styled login/logout pages) matching the storefront's pastel palette
- Full CRUD across Products, Orders, Order Updates, Contacts, Blog Posts, and Comments

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django (4.2–6.x), Python |
| Frontend | Bootstrap 5, vanilla JS/jQuery, Playfair Display + Poppins |
| Database | SQLite (dev) → PostgreSQL via `dj-database-url` (prod) |
| Payments | Razorpay |
| PDF generation | ReportLab |
| Static/media | WhiteNoise |
| Admin theming | django-jazzmin + custom CSS overrides |
| Deployment | Render (Gunicorn) |

---

## Project Structure

```
oqirel/
├── MAC/                      # Project configuration
│   ├── settings.py           # Env-var-driven config (see below)
│   ├── urls.py
│   └── wsgi.py
├── shop/                     # Core e-commerce app
│   ├── models.py             # Product, Order, OrderUpdate, Contact, Wishlist
│   ├── views.py
│   ├── admin.py
│   ├── templates/shop/
│   └── static/shop/
├── blog/                     # Blog app
│   ├── models.py             # BlogPost, BlogComment
│   ├── views.py
│   └── templates/blog/
├── templates/admin/          # Custom admin login/logout overrides
├── media/                    # User-uploaded product images
├── requirements.txt
└── manage.py
```

---

## Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/Nehaa2509/my_awesome_cart.git
cd my_awesome_cart

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root (never commit this):

```
SECRET_KEY=your-strong-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

`settings.py` reads all of these via `os.environ.get(...)` with safe local-dev fallbacks — for any real or public deployment, set `DEBUG=False` and provide real values for every variable above through your host's environment variable dashboard, not the `.env` file.

### Database & run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

---

## Deployment (Render)

- **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start command:** `gunicorn MAC.wsgi:application`
- Set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (include your `.onrender.com` domain), `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET` as environment variables on the Render dashboard
- If using PostgreSQL in production, also set `DATABASE_URL` (read via `dj-database-url`)

---

## Security notes

- Cart totals and stock are always re-verified server-side at checkout — client-submitted values are discarded, not trusted
- Invoice downloads require authentication and an ownership check (account match, verified email match, or staff) before serving the PDF
- Stock updates use atomic `F()` expressions to avoid race conditions during concurrent purchases
- Secrets are read from environment variables with local-only fallback defaults — production deployments must override every credential

---

## Roadmap

- [ ] Move `OrderUpdate.order_id` from a plain integer to a proper `ForeignKey('Order')` for referential integrity
- [ ] Add a `created_at` timestamp to `Order` for chronological sorting/filtering in admin
- [ ] Email notifications on order placement and status changes
- [ ] Pagination for the product catalog and blog feed
- [ ] Rate-limiting on the order tracker to prevent order ID/email enumeration

---

## License

Educational/portfolio project. Feel free to fork and build on it.
