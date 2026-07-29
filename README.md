# 🛒 OQIREL — Premium Ambient Accords

A full-featured **Django e-commerce web application** for premium ambient accords, handcrafted soy candles, diffusers, and botanical skincare. Features dynamic product slideshows, interactive glassmorphism UI, client-side cart with session persistence, Razorpay payment gateway integration, order tracking, blog journal, wishlist management, downloadable PDF invoices, and a custom boutique admin panel.

🌐 **Live Website**: [https://oqirel-project.onrender.com](https://oqirel-project.onrender.com)  
📦 **GitHub Repository**: [https://github.com/Nehaa2509/oqirel-project.git](https://github.com/Nehaa2509/oqirel-project.git)

---

## ✨ Key Features

- 🌌 **Cinematic Hero & Landing Page** — Interactive 3D anti-gravity parallax backdrop with particle atmospheric drift.
- 🛍️ **Boutique Catalog** — Category-wise dynamic product collections with interactive glassmorphism cards.
- 🔍 **Live Search & Autocomplete** — Instant AJAX search results for quick product discovery.
- 🛒 **Shopping Cart & Wishlist** — Client-side cart with quantity controls and user wishlist persistence.
- 💳 **Razorpay Payment Gateway** — Seamless online payment checkout with cryptographic signature verification.
- 📦 **Order Tracking** — Track order lifecycle by Order ID and Email verification.
- 📄 **PDF Invoice Generation** — Instant downloadable PDF receipts tailored to the OQIREL brand theme.
- 📝 **Editorial Journal & Blog** — Curated articles with comments and author profiles.
- 🎨 **Custom Boutique Admin** — Styled Django Admin powered by Jazzmin with custom color palette.

---

## 📁 Project Structure

`
oqirel-project/
├── MAC/                    # Main application configuration (settings, urls, wsgi)
├── shop/                   # Core store app (views, models, templates, static assets)
├── blog/                   # Blog app (models, templates, views)
├── templates/              # Shared admin & system templates
├── media/                  # Product images & media assets
├── static/                 # CSS & JS static assets
├── manage.py               # Django management CLI
├── populate_db.py          # Database seeding script
├── Procfile                # Gunicorn deployment config for Render
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
`

---

## 🚀 Quick Start (Local Setup)

1. **Clone the repository:**
   `ash
   git clone https://github.com/Nehaa2509/oqirel-project.git
   cd oqirel-project
   `

2. **Create and activate virtual environment:**
   `ash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   `

3. **Install dependencies:**
   `ash
   pip install -r requirements.txt
   `

4. **Run migrations & seed database:**
   `ash
   python manage.py migrate
   python populate_db.py
   `

5. **Start development server:**
   `ash
   python manage.py runserver
   `
   Open http://127.0.0.1:8000/ in your browser.

---

## 🌐 Live Deployment

- **Live Site**: [https://oqirel-project.onrender.com](https://oqirel-project.onrender.com)
- **Source Code**: [https://github.com/Nehaa2509/oqirel-project.git](https://github.com/Nehaa2509/oqirel-project.git)