Markdown
# 🛒 MyAwesomeCart

A full-featured **Django e-commerce web application** with a shopping cart, Razorpay payment integration, order tracking, and a blog — built as a learning project inspired by the *Code With Harry* Django series.

---

## ✨ Features

- 🏠 **Landing Page** — Clean home page with navigation to the shop
- 📦 **Product Catalog** — Category-wise dynamic product slideshows
- 🔍 **Product Detail View** — Individual product pages
- 🛒 **Shopping Cart** — Client-side cart with session persistence
- 💳 **Razorpay Payment Gateway** — Secure online payments with signature verification
- 📊 **Order Management** — Orders saved to DB with payment status tracking (`Pending` ➡️ `Paid` / `Failed`)
- 📍 **Order Tracker** — Track order status by Order ID + Email
- 📝 **Blog** — Blog posts with thumbnails, content, and author info
- ✉️ **Contact Form** — Saves messages from visitors to the database
- 🛠️ **Django Admin** — Full admin panel for managing all models

---

## 📂 Project Structure

MyAwesomeCart/                  # Django project root
├── MAC/                        # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── shop/                       # Main e-commerce app
│   ├── models.py               # Product, Contact, Order, OrderUpdate
│   ├── views.py                # All shop views
│   ├── urls.py                 # Shop URL patterns
│   ├── admin.py                # Admin registrations
│   ├── templates/shop/         # HTML templates
│   └── static/                 # CSS, JS, images
├── blog/                       # Blog app
│   ├── models.py               # Blogpost model
│   ├── views.py
│   ├── urls.py
│   └── templates/blog/
├── media/                      # User-uploaded media files
├── db.sqlite3                  # SQLite database
├── manage.py
└── populate_db.py              # Script to seed initial data


---

## 🗃️ Data Models

### `shop` App

| Model | Key Fields |
| :--- | :--- |
| `Product` | `product_name`, `category`, `subcategory`, `price`, `description`, `image` |
| `Contact` | `name`, `email`, `phone`, `desc` |
| `Order` | `items_json`, `name`, `email`, `address`, `amount`, `payment_status`, Razorpay IDs |
| `OrderUpdate` | `order_id`, `update_desc`, `timestamp` |

### `blog` App

| Model | Key Fields |
| :--- | :--- |
| `Blogpost` | `title`, `chead`, `author`, `content`, `pub_date`, `thumbnail` |

---

## 🛣️ URL Routes

| URL Pattern | View | Description |
| :--- | :--- | :--- |
| `/` | `home` | Landing page |
| `/shop/` | `index` | Product catalog |
| `/shop/about/` | `about` | About page |
| `/shop/contact/` | `contact` | Contact form |
| `/shop/tracker/` | `tracker` | Order tracking |
| `/shop/search/` | `search` | Search page |
| `/shop/products/<id>` | `productview` | Product detail |
| `/shop/checkout/` | `checkout` | Checkout & Razorpay init |
| `/shop/handlerequest/` | `handlerequest` | Razorpay payment callback |
| `/blog/` | Blog views | Blog listing & detail |
| `/admin/` | Django Admin | Admin panel |

---

## 💳 Payment Flow (Razorpay)

User fills checkout form
⬇️
Order saved to DB (status: Pending)
⬇️
Razorpay order created via API
⬇️
User pays via Razorpay modal (pay.html)
⬇️
Razorpay POSTs to /shop/handlerequest/
⬇️
Signature verified on backend
⬇️
Order status updated ➡️ "Paid" or "Failed"


---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd MyAwesomeCart

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate    
# Linux/macOS
# source venv/bin/activate   

# 3. Install dependencies
pip install django razorpay pillow

# 4. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create a superuser (for admin panel)
python manage.py createsuperuser

# 6. (Optional) Seed the database with sample data
python populate_db.py

# 7. Run the development server
python manage.py runserver
Visit http://127.0.0.1:8000/ in your browser.

⚙️ Configuration
Open MAC/settings.py and update the following configuration properties before pushing live:

Python
# Replace with your actual Razorpay credentials
RAZORPAY_KEY_ID     = 'your_razorpay_key_id'
RAZORPAY_KEY_SECRET = 'your_razorpay_key_secret'

# Generate a new secret key for production
SECRET_KEY = 'your-strong-secret-key'

# Disable debug mode in production
DEBUG = False

# Add your domain/IP
ALLOWED_HOSTS = ['yourdomain.com']
⚠️ Warning: Never commit your real SECRET_KEY or Razorpay credentials directly to version control. Always pull them from environment variables or a secure .env file instead.

📦 Dependencies
Package	Purpose
django	Web framework (Django>=5.0)
razorpay	Payment gateway Python SDK
pillow	Image handling support for model ImageField
👑 Admin Panel
Access the Django admin portal at http://127.0.0.1:8000/admin/ to:

Add / edit / delete Products

View Orders and alter settlement flags

Log dynamic Order Updates tracking metrics

Manage Blog Posts

Track incoming client Contact notes

🚀 Future Improvements
[ ] User authentication & account dashboard

[ ] Wishlist / favourites functionality

[ ] Product search with filtering & sorting

[ ] Email notifications on order placement

[ ] Pagination for product catalog and blog

[ ] Deploy to production (Render / Railway / VPS)

[ ] Move to PostgreSQL for production database

🤝 Credits
Built following the structural principles taught in the Code With Harry Django development series.

📄 License
This project is open-source and intended for educational purposes. Feel free to fork and build upon it!
