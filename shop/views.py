import json
import math
import os
import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Contact, Order, OrderUpdate, Wishlist
from .utils import generate_invoice_pdf

# Helper to dynamically retrieve active Razorpay Client credentials
def get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', None) or os.environ.get('RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None) or os.environ.get('RAZORPAY_KEY_SECRET', '')
    return razorpay.Client(auth=(key_id, key_secret))

# 1. Main Shop Homepage View (Category-Wise Dynamic Slideshows)
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + math.ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    context = {'allProds': allProds}
    if len(allProds) == 0 or len(allProds[0][0]) == 0:
        context['message'] = "No products found in the store."
    # Pass wishlist product IDs for heart button state
    if request.user.is_authenticated:
        context['wishlist_ids'] = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        context['wishlist_ids'] = set()
    return render(request, 'shop/index.html', context)

def searchMatch(query, item):
    if query.lower() in item.product_name.lower() or query.lower() in item.description.lower() or query.lower() in item.category.lower(): 
        return True
    else:
        return False
     
def search(request):
    query = request.GET.get('query', '')
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if is_ajax:
        results = []
        if query and len(query.strip()) > 0:
            all_products = Product.objects.all()
            matching_products = [item for item in all_products if searchMatch(query, item)]
            for p in matching_products:
                results.append({
                    'id': p.id,
                    'product_name': p.product_name,
                    'category': p.category,
                    'price': p.price,
                    'image': f"/media/{p.image}" if p.image else ""
                })
        return JsonResponse({'products': results, 'query': query})

    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]   
        n = len(prod)
        nSlides = n // 4 + math.ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])

    context = {'allProds': allProds}
    
    if len(allProds) == 0:
        context['message'] = "Please match your query correctly. No products found matching your search criteria."
        
    return render(request, 'shop/search.html', context)

# 1.5 Main Landing Page View
def home(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + math.ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    context = {'allProds': allProds}
    if len(allProds) == 0 or len(allProds[0][0]) == 0:
        context['message'] = "No products found in the store."
    if request.user.is_authenticated:
        context['wishlist_ids'] = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        context['wishlist_ids'] = set()
    return render(request, 'shop/home_catalog.html', context)

# 2. About Page View
def about(request):
    return render(request, 'shop/about.html')

# 3. Order Tracking View (Requires dual Order ID + matching Email parameter to prevent enumeration/leaks)
def tracker(request):
    if request.method == "POST":    
        orderId = request.POST.get('orderId', '').strip()
        email = request.POST.get('email', '').strip().lower()
        
        if not orderId or not email:
            return HttpResponse('{}', content_type="application/json")
            
        try:
            orders = Order.objects.filter(order_id=orderId)
            matching_order = None
            for o in orders:
                if o.email and o.email.strip().lower() == email:
                    matching_order = o
                    break
            
            if matching_order:
                try:
                    updates = OrderUpdate.objects.filter(order_id=orderId)
                    update_list = []
                    for item in updates:
                        update_list.append({'text': item.update_desc, 'time': str(item.timestamp)})
                except Exception:
                    update_list = [{'text': 'Your order has been placed successfully!', 'time': 'Just now'}]
                
                response_data = [update_list, matching_order.items_json]
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse('{}', content_type="application/json")
                
        except Exception:
            return HttpResponse('{}', content_type="application/json")
            
    return render(request, 'shop/tracker.html')

# 5. Product Detail View
def productview(request, myid):
    product = get_object_or_404(Product, id=myid)
    
    # Atomic View Count Increment
    Product.objects.filter(id=myid).update(views=F('views') + 1)
    product.refresh_from_db()
    
    recommendations = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by('-views', '-id')[:4]
    
    context = {
        'product': product,
        'recommendations': recommendations
    }
    return render(request, 'shop/productView.html', context)

# 6. Checkout View (Secured via Native Session Authentication Guard + Authoritative Server-Side Pricing & Stock Validation)
@login_required(login_url='/shop/login/')
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        total_price = 0
        sanitized_cart = {}

        # Authoritative Server-Side Price & Stock Validation
        try:
            raw_cart = json.loads(items_json)
            if not raw_cart:
                messages.error(request, "Your cart is currently empty!")
                return redirect('/shop/checkout/')

            for key, item in raw_cart.items():
                qty = int(item[0])
                if qty <= 0:
                    continue

                clean_id_str = str(key).replace('pr', '').strip()
                if not clean_id_str.isdigit():
                    messages.error(request, f"Invalid product format in cart for key: {key}")
                    return redirect('/shop/checkout/')

                prod_id = int(clean_id_str)

                try:
                    product = Product.objects.get(id=prod_id)
                except Product.DoesNotExist:
                    messages.error(request, f"Product ID #{prod_id} does not exist in our system catalog.")
                    return redirect('/shop/checkout/')

                if qty > product.stock:
                    messages.error(request, f"Insufficient stock for '{product.product_name}'. Only {product.stock} available.")
                    return redirect('/shop/checkout/')

                total_price += qty * product.price
                sanitized_cart[key] = [qty, product.product_name, product.price]

        except (json.JSONDecodeError, TypeError, ValueError, IndexError):
            messages.error(request, "Cart payload validation failed. Please try again.")
            return redirect('/shop/checkout/')

        sanitized_items_json = json.dumps(sanitized_cart)

        order = Order(
            user=request.user if request.user.is_authenticated else None,
            items_json=sanitized_items_json,
            name=name, email=email, 
            address1=address1, address2=address2, city=city, 
            state=state, zip_code=zip_code, phone=phone, amount=total_price,
            payment_status="Pending"
        )
        order.save()
        
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been placed..!")
        update.save()
        
        razorpay_amount = int(total_price * 100)
        data = {
            "amount": razorpay_amount,
            "currency": "INR",
            "receipt": str(order.order_id)
        }
        
        try:
            client = get_razorpay_client()
            razorpay_order = client.order.create(data=data)
            order.razorpay_order_id = razorpay_order['id']
            order.save()
        except Exception as e:
            return HttpResponse(f"Error creating Razorpay order: {str(e)}")

        callback_url = request.build_absolute_uri('/shop/handlerequest/')
        context = {
            'razorpay_order_id': order.razorpay_order_id,
            'amount': razorpay_amount,
            'key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
            'callback_url': callback_url,
            'name': name,
            'email': email,
            'phone': phone,
            'order_id': order.order_id,
        }
        return render(request, 'shop/pay.html', context)

    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client = get_razorpay_client()
            client.utility.verify_payment_signature(params_dict)
            
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = "Paid"
            order.save()
            
            try:
                cart = json.loads(order.items_json)
                for key, item in cart.items():
                    prod_id = int(str(key).replace('pr', '').strip())
                    qty = int(item[0])
                    Product.objects.filter(id=prod_id).update(stock=F('stock') - qty)
            except Exception as stock_err:
                print(f"Stock decrement error for order #{order.order_id}: {stock_err}")

            update = OrderUpdate(order_id=order.order_id, update_desc="The Order payment has been successfully received!")
            update.save()
            
            return render(request, 'shop/checkout.html', {'thank': True, 'id': order.order_id, 'order': order})
            
        except Exception as e:
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.payment_status = "Failed"
                order.save()
            except Exception:
                pass
            messages.error(request, f"Payment verification failed! Details: {str(e)}")
            return redirect('/shop/checkout/')
            
    return redirect('/shop/')

# 6.5 Download Invoice View Endpoint (Secured against IDOR with @login_required & Ownership Verification)
@login_required(login_url='/shop/login/')
def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    # Ownership Security Check: user FK match OR email string match (case-insensitive) OR staff
    user_email_match = bool(
        order.email and request.user.email and 
        order.email.strip().lower() == request.user.email.strip().lower()
    )
    user_fk_match = bool(order.user_id is not None and order.user_id == request.user.id)
    
    is_owner = user_fk_match or user_email_match or request.user.is_staff
    
    if not is_owner:
        return HttpResponseForbidden("Access Denied: You are not authorized to view this invoice.")
        
    pdf_buffer = generate_invoice_pdf(order)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_Order_{order.order_id}.pdf"'
    return response

# 7. Contact Us View
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('desc', '') 
        
        contact_entry = Contact(name=name, email=email, phone=phone, desc=message)
        contact_entry.save()
        
        return render(request, 'shop/contact.html', {'thank': True})
        
    return render(request, 'shop/contact.html')

# =========================================================================
# AUTHENTICATION VIEWS (LOGIN, SIGNUP, LOGOUT)
# =========================================================================
def login_page(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/shop/checkout/'
    
    if request.method == 'POST':
        username = request.POST.get('loginUsername', '').strip()
        password = request.POST.get('loginPassword', '').strip()

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'shop/login.html', {'next': next_url})

def signup_page(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/shop/checkout/'
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        pass1 = request.POST.get('pass1', '').strip()
        pass2 = request.POST.get('pass2', '').strip()

        if pass1 != pass2:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'shop/signup.html', {'next': next_url})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken. Choose another username.")
            return render(request, 'shop/signup.html', {'next': next_url})

        new_user = User.objects.create_user(username, email, pass1)
        new_user.save()
        login(request, new_user)
        messages.success(request, "Your account has been created successfully!")
        return redirect(next_url)

    return render(request, 'shop/signup.html', {'next': next_url})

def handleLogout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return render(request, 'shop/logged_out.html')


# =========================================================================
# ❤️ Wishlist Views
# =========================================================================

@login_required(login_url='/shop/login/')
def wishlist_toggle(request, product_id):
    """Toggle a product in the user's wishlist (add if not present, remove if present)."""
    product = get_object_or_404(Product, id=product_id)
    entry, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        entry.delete()
        is_wishlisted = False
    else:
        is_wishlisted = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'wishlisted': is_wishlisted})

    return redirect(request.META.get('HTTP_REFERER', '/shop/'))


@login_required(login_url='/shop/login/')
def wishlist_page(request):
    """Render the user's wishlist page."""
    items = Wishlist.objects.filter(user=request.user).select_related('product').order_by('-added_at')
    return render(request, 'shop/wishlist.html', {'wishlist_items': items})


@login_required(login_url='/shop/login/')
def wishlist_remove(request, product_id):
    """Remove a specific product from wishlist (POST only)."""
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, "Removed from your wishlist.")
    return redirect('wishlist')