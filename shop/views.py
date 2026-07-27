import json  # FIXED: Handles JSON tracking payloads cleanly
import math
import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from .models import Product, Contact, Order, OrderItem, OrderUpdate  # FIXED: Unified models
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
    if query.lower() in item.product_name.lower() or query.lower() in item.description.lower(): 
        return True
    else:
        return False
     
def search(request):
    query = request.GET.get('query', '')
    
    # Instant Search AJAX handler
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results = []
        if len(query) > 0:
            products = Product.objects.all()
            for item in products:
                if searchMatch(query, item):
                    results.append({
                        'id': item.id,
                        'product_name': item.product_name,
                        'category': item.category,
                        'price': item.price,
                        'image': item.image.url if item.image else ''
                    })
        return HttpResponse(json.dumps(results), content_type="application/json")
        
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
    return render(request, 'shop/home.html')

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
    
    # Increment views count
    product.views += 1
    product.save()
    
    # Fetch top 4 recommended products in the same category
    recommendations = Product.objects.filter(category=product.category).exclude(id=product.id).order_by('-views')[:4]
    
    return render(request, 'shop/productView.html', {'product': product, 'recommendations': recommendations})

# 6. Checkout View
@login_required(login_url='/shop/login/')
def checkout(request):
    if request.method == "POST":
        try:
            is_json = request.content_type == 'application/json'
            if is_json:
                data = json.loads(request.body)
                client_cart = data.get('cart', {})
                name = data.get('name', '').strip()
                email = data.get('email', '').strip()
                address1 = data.get('address1', '').strip()
                address2 = data.get('address2', '').strip()
                city = data.get('city', '').strip()
                state = data.get('state', '').strip()
                zip_code = data.get('zip_code', '').strip()
                phone = data.get('phone', '').strip()
                items_json = json.dumps(client_cart)
            else:
                items_json = request.POST.get('itemsJson', '')
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                address1 = request.POST.get('address1', '').strip()
                address2 = request.POST.get('address2', '').strip()
                city = request.POST.get('city', '').strip()
                state = request.POST.get('state', '').strip()
                zip_code = request.POST.get('zip_code', '').strip()
                phone = request.POST.get('phone', '').strip()
                
                raw_cart = json.loads(items_json) if items_json else {}
                client_cart = {}
                for k, v in raw_cart.items():
                    prod_id = str(k).replace("pr", "")
                    qty = v[0] if isinstance(v, list) else v
                    client_cart[prod_id] = qty

            if not client_cart:
                if is_json:
                    return JsonResponse({'error': 'Your cart is completely empty.'}, status=400)
                return render(request, 'shop/checkout.html', {'error': 'Your cart is empty.'})

            product_ids = [str(k) for k in client_cart.keys()]
            
            with transaction.atomic():
                products = Product.objects.filter(id__in=product_ids)
                product_map = {str(p.id): p for p in products}

                total_amount = 0
                items_to_create = []

                for prod_id, qty in client_cart.items():
                    qty = int(qty)
                    if qty <= 0:
                        continue
                        
                    product = product_map.get(str(prod_id))
                    if not product:
                        if is_json:
                            return JsonResponse({'error': f'Product Reference ID {prod_id} is missing.'}, status=400)
                        continue

                    item_total = product.price * qty
                    total_amount += item_total
                    
                    items_to_create.append({
                        'product': product,
                        'quantity': qty,
                        'price': product.price
                    })

                if total_amount == 0 and is_json:
                    return JsonResponse({'error': 'Invalid items selected.'}, status=400)

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    items_json=items_json,
                    name=name,
                    email=email,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    phone=phone,
                    amount=total_amount,
                    payment_status="Pending"
                )

                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price_at_purchase=item['price']
                    ) for item in items_to_create
                ])

                OrderUpdate.objects.create(order_id=order.order_id, update_desc="The Order has been placed..!")

            # Razorpay order creation (in paise)
            razorpay_amount = int(total_amount * 100)
            razorpay_order = client.order.create(data={
                "amount": razorpay_amount,
                "currency": "INR",
                "receipt": f"receipt_order_{order.order_id}",
                "payment_capture": 1
            })
            
            order.razorpay_order_id = razorpay_order['id']
            order.save(update_fields=['razorpay_order_id'])

            if is_json:
                return JsonResponse({
                    'success': True,
                    'order_id': order.order_id,
                    'razorpay_order_id': order.razorpay_order_id,
                    'amount': razorpay_amount,
                    'razorpay_key': getattr(settings, 'RAZORPAY_KEY_ID', '')
                })

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

        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'error': f'Checkout error: {str(e)}'}, status=500)
            return HttpResponse(f"Error creating order: {str(e)}")

    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            internal_order_id = data.get('order_id')

            # Build formal parameters checklist for validation engine
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            # Cryptographic identity validation check using Razorpay Client utils
            client.utility.verify_payment_signature(params_dict)

            # Retrieve internal records matching payment tracking specifications
            if internal_order_id:
                order = Order.objects.get(order_id=internal_order_id, razorpay_order_id=razorpay_order_id)
            else:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            
            # Update fulfillment status across system layers atomically
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = "Completed"
            order.save(update_fields=['razorpay_payment_id', 'razorpay_signature', 'payment_status'])

            update = OrderUpdate(order_id=order.order_id, update_desc="The Order payment has been successfully received!")
            update.save()

            # Render the relational PDF buffer created in utils.py
            pdf_buffer = generate_invoice_pdf(order)
            
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_BWD_{order.order_id}.pdf"'
            return response

        except razorpay.errors.SignatureVerificationError:
            if 'internal_order_id' in locals() and internal_order_id:
                Order.objects.filter(order_id=internal_order_id).update(payment_status="Failed")
            return JsonResponse({'success': False, 'error': 'Security signature check rejected.'}, status=400)
            
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Target order configuration untraceable.'}, status=404)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return HttpResponse("Method Not Allowed", status=405)

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

# 8. Authentication Views
def handle_signup(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        pass1 = request.POST.get('pass1', '')
        pass2 = request.POST.get('pass2', '')
        
        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect('/shop/signup/')
            
        try:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.save()
            messages.success(request, "Your account has been successfully created. Please login.")
            return redirect('/shop/login/')
        except Exception:
            messages.error(request, "Username already taken or invalid details")
            return redirect('/shop/signup/')
            
    return render(request, 'shop/signup.html')

def handle_login(request):
    if request.method == "POST":
        loginusername = request.POST.get('loginusername', '')
        loginpassword = request.POST.get('loginpassword', '')
        next_url = request.POST.get('next', '/shop/')
        
        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully logged in")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials, please try again")
            return redirect(f'/shop/login/?next={next_url}')
            
    next_url = request.GET.get('next', '/shop/')
    return render(request, 'shop/login.html', {'next': next_url})

def handle_logout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('/shop/')