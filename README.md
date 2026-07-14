<?xml version="1.0" encoding="UTF-8"?>
<project name="MyAwesomeCart">
    <description>A full-featured Django e-commerce web application with a shopping cart, Razorpay payment integration, order tracking, and a blog — built as a learning project inspired by the Code With Harry Django series.</description>
    
    <features>
        <feature icon="🏠" name="Landing Page">Clean home page with navigation to the shop</feature>
        <feature icon="📦" name="Product Catalog">Category-wise dynamic product slideshows</feature>
        <feature icon="🔍" name="Product Detail View">Individual product pages</feature>
        <feature icon="🛒" name="Shopping Cart">Client-side cart with session persistence</feature>
        <feature icon="💳" name="Razorpay Payment Gateway">Secure online payments with signature verification</feature>
        <feature icon="📊" name="Order Management">Orders saved to DB with payment status tracking (Pending to Paid / Failed)</feature>
        <feature icon="📍" name="Order Tracker">Track order status by Order ID + Email</feature>
        <feature icon="📝" name="Blog">Blog posts with thumbnails, content, and author info</feature>
        <feature icon="✉️" name="Contact Form">Saves messages from visitors to the database</feature>
        <feature icon="🛠️" name="Django Admin">Full admin panel for managing all models</feature>
    </features>

    <projectStructure>
        <dir name="MyAwesomeCart">
            <dir name="MAC">
                <file name="settings.py" />
                <file name="urls.py" />
                <file name="wsgi.py" />
                <file name="asgi.py" />
            </dir>
            <dir name="shop">
                <file name="models.py" />
                <file name="views.py" />
                <file name="urls.py" />
                <file name="admin.py" />
                <dir name="templates">
                    <dir name="shop" />
                </dir>
                <dir name="static" />
            </dir>
            <dir name="blog">
                <file name="models.py" />
                <file name="views.py" />
                <file name="urls.py" />
                <dir name="templates">
                    <dir name="blog" />
                </dir>
            </dir>
            <dir name="media" />
            <file name="db.sqlite3" />
            <file name="manage.py" />
            <file name="populate_db.py" />
        </dir>
    </projectStructure>

    <dataModels>
        <app name="shop">
            <model name="Product">
                <fields>product_name, category, subcategory, price, description, image</fields>
            </model>
            <model name="Contact">
                <fields>name, email, phone, desc</fields>
            </model>
            <model name="Order">
                <fields>items_json, name, email, address, amount, payment_status, Razorpay IDs</fields>
            </model>
            <model name="OrderUpdate">
                <fields>order_id, update_desc, timestamp</fields>
            </model>
        </app>
        <app name="blog">
            <model name="Blogpost">
                <fields>title, chead, author, content, pub_date, thumbnail</fields>
            </model>
        </app>
    </dataModels>

    <urlRoutes>
        <route pattern="/" view="home" description="Landing page" />
        <route pattern="/shop/" view="index" description="Product catalog" />
        <route pattern="/shop/about/" view="about" description="About page" />
        <route pattern="/shop/contact/" view="contact" description="Contact form" />
        <route pattern="/shop/tracker/" view="tracker" description="Order tracking" />
        <route pattern="/shop/search/" view="search" description="Search page" />
        <route pattern="/shop/products/&lt;id&gt;" view="productview" description="Product detail" />
        <route pattern="/shop/checkout/" view="checkout" description="Checkout &amp; Razorpay init" />
        <route pattern="/shop/handlerequest/" view="handlerequest" description="Razorpay payment callback" />
        <route pattern="/blog/" view="Blog views" description="Blog listing &amp; detail" />
        <route pattern="/admin/" view="Django Admin" description="Admin panel" />
    </urlRoutes>

    <paymentFlow gateway="Razorpay">
        <step order="1">User fills checkout form</step>
        <step order="2">Order saved to DB (status: Pending)</step>
        <step order="3">Razorpay order created via API</step>
        <step order="4">User pays via Razorpay modal (pay.html)</step>
        <step order="5">Razorpay POSTs to /shop/handlerequest/</step>
        <step order="6">Signature verified on backend</step>
        <step order="7">Order status updated to 'Paid' or 'Failed'</step>
    </paymentFlow>

    <setupInstructions>
        <prerequisites>
            <item>Python 3.10+</item>
            <item>pip</item>
        </prerequisites>
        <steps>
            <step order="1" cmd="git clone &lt;your-repo-url&gt; &amp;&amp; cd MyAwesomeCart">Clone the repository and access the root directory</step>
            <step order="2" cmd="python -m venv venv">Create virtual environment</step>
            <step order="3" cmd="venv\Scripts\activate">Activate environment (Windows)</step>
            <step order="4" cmd="pip install django razorpay pillow">Install project dependencies</step>
            <step order="5" cmd="python manage.py makemigrations &amp;&amp; python manage.py migrate">Generate and apply database tables</step>
            <step order="6" cmd="python manage.py createsuperuser">Create portal administrative user</step>
            <step order="7" cmd="python populate_db.py">Seed database tables with sample data</step>
            <step order="8" cmd="python manage.py runserver">Boot up development application network link at http://127.0.0.1:8000/</step>
        </steps>
    </setupInstructions>

    <dependencies>
        <package name="django" version="&gt;=5.0" purpose="Web framework" />
        <package name="razorpay" version="latest" purpose="Payment gateway Python SDK" />
        <package name="pillow" version="latest" purpose="Image handling support for model ImageField" />
    </dependencies>

    <productionConfiguration warning="Never commit real keys or credentials directly to version control. Always pull from environment variables or a secure .env file.">
        <setting key="DEBUG">False</setting>
        <setting key="ALLOWED_HOSTS">['yourdomain.com']</setting>
        <setting key="SECRET_KEY">your-strong-secret-key</setting>
        <setting key="RAZORPAY_KEY_ID">your_razorpay_key_id</setting>
        <setting key="RAZORPAY_KEY_SECRET">your_razorpay_key_secret</setting>
    </productionConfiguration>

    <futureImprovements>
        <item status="pending">User authentication &amp; account dashboard</item>
        <item status="pending">Wishlist / favourites functionality</item>
        <item status="pending">Product search with filtering &amp; sorting</item>
        <item status="pending">Email notifications on order placement</item>
        <item status="pending">Pagination for product catalog and blog</item>
        <item status="pending">Deploy to production (Render / Railway / VPS)</item>
        <item status="pending">Move to PostgreSQL for production database</item>
    </futureImprovements>

    <credits>Built following the structural principles taught in the Code With Harry Django development series.</credits>
    <license type="educational">This project is open-source and intended for educational purposes. Feel free to fork and build upon it!</license>
</project>
