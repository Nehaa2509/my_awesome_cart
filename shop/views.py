import json  # FIXED: Handles JSON tracking payloads cleanly
import math
import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Contact, Order, OrderUpdate  # FIXED: Unified to use 'Order' consistently
from .utils import generate_invoice_pdf

# Initialize Razorpay Client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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
    return render(request, 'shop/index.html', context)

def searchMatch(query, item):
    if query.lower() in item.product_name.lower() or query.lower() in item.description.lower() or query.lower() in item.category.lower(): 
        return True
    else:
        return False
     
def search(request):
    query = request.GET.get('query', '')
    
    # Handle AJAX / Fetch requests for instant search autocomplete
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
    
    # NEW FEATURE: Injects the error message flag if no query results match
    if len(allProds) == 0:
        context['message'] = "Please match your query correctly. No products found matching your search criteria."
        
    return render(request, 'shop/search.html', context)

# 1.5 Main Landing Page View
def home(request):
    return index(request)

# 2. About Page View
def about(request):
    return render(request, 'shop/about.html')

# 3. Order Tracking View
def tracker(request):
    if request.method == "POST":    
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            
            if len(order) > 0:
                try:
                    updates = OrderUpdate.objects.filter(order_id=orderId)
                    update_list = []
                    for item in updates:
                        update_list.append({'text': item.update_desc, 'time': str(item.timestamp)})
                except Exception:
                    update_list = [{'text': 'Your order has been placed successfully!', 'time': 'Just now'}]
                
                # FIXED: Safely passing the string-serialized 'update_list' array directly down
                response_data = [update_list, order[0].items_json]
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse('{}', content_type="application/json")
                
        except Exception as e:
            return HttpResponse('{}', content_type="application/json")
            
    return render(request, 'shop/tracker.html')

# 5. Product Detail View
def productview(request, myid):
    product = get_object_or_404(Product, id=myid)
    
    # 1. Atomic View Count Increment
    Product.objects.filter(id=myid).update(views=F('views') + 1)
    product.refresh_from_db()
    
    # 2. Django ORM Query: Pull top 4 recommended items in the same category (excluding current item)
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

# 6. Checkout View (Secured via Native Session Authentication Guard)
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

        # Calculate total price on the backend
        total_price = 0
        try:
            cart = json.loads(items_json)
            for item in cart.values():
                qty = item[0]
                price = item[2]
                total_price += qty * price
        except Exception:
            total_price = 0

        # Save the order to the database with amount and payment_status Pending
        order = Order(items_json=items_json, name=name, email=email, 
                      address1=address1, address2=address2, city=city, 
                      state=state, zip_code=zip_code, phone=phone, amount=total_price,
                      payment_status="Pending")
        order.save()
        
        # Initialize the baseline milestone tracker data update record
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been placed..!")
        update.save()
        
        # Create Razorpay order (amount in paise)
        razorpay_amount = int(total_price * 100)
        data = {
            "amount": razorpay_amount,
            "currency": "INR",
            "receipt": str(order.order_id)
        }
        
        try:
            razorpay_order = client.order.create(data=data)
            order.razorpay_order_id = razorpay_order['id']
            order.save()
        except Exception as e:
            return HttpResponse(f"Error creating Razorpay order: {str(e)}")

        callback_url = request.build_absolute_uri('/shop/handlerequest/')
        context = {
            'razorpay_order_id': order.razorpay_order_id,
            'amount': razorpay_amount,
            'key_id': settings.RAZORPAY_KEY_ID,
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
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            
            # If signature verified, find the order and mark as Paid
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = "Paid"
            order.save()
            
            # Create payment update record
            update = OrderUpdate(order_id=order.order_id, update_desc="The Order payment has been successfully received!")
            update.save()
            
            # Generate PDF invoice and return as downloadable attachment
            pdf_buffer = generate_invoice_pdf(order)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_Order_{order.order_id}.pdf"'
            return response
            
        except Exception as e:
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.payment_status = "Failed"
                order.save()
            except Exception:
                pass
            return HttpResponse(f"Payment verification failed! Error: {str(e)}")
            
    return HttpResponse("Invalid request method.")

# 6.5 Download Invoice View Endpoint
def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
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

        # Create new user
        new_user = User.objects.create_user(username, email, pass1)
        new_user.save()
        login(request, new_user)
        messages.success(request, "Your account has been created successfully!")
        return redirect(next_url)

    return render(request, 'shop/signup.html', {'next': next_url})

def handleLogout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('/shop/')