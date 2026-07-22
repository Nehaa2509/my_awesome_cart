import json  # FIXED: Added missing import for handling JSON tracking payloads
import math
import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Contact, Order, OrderUpdate  # FIXED: Unified to use 'Order' consistently

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
    return render(request, 'shop/index.html', context)

def searchMatch(query, item):
    return query.lower() in item.product_name.lower() or query.lower() in item.description.lower()

def search(request):
    query = request.GET.get('query', '')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]   
        n = len(prod)
        nSlides = n // 4 + math.ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    context = {'allProds': allProds}
    return render(request, 'shop/index.html', context)

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
                
                # FIXED: Now dumping 'update_list' (the dictionary array) instead of the raw 'updates' model objects collection
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
    return render(request, 'shop/productView.html', {'product': product})

# 6. Checkout View
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
            
            return render(request, 'shop/checkout.html', {'thank': True, 'id': order.order_id})
            
        except Exception as e:
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.payment_status = "Failed"
                order.save()
            except Exception:
                pass
            return HttpResponse(f"Payment verification failed! Error: {str(e)}")
            
    return HttpResponse("Invalid request method.")

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