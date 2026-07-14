from django.db import models

# 1. Product Model
class Product(models.Model):
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    description = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.product_name 


# 2. Contact Model
class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=15, default="")  
    desc = models.CharField(max_length=500, default="")  

    def __str__(self):
        return self.name


# 3. Orders Model (FIXED SYNTAX)
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)       
    items_json = models.CharField(max_length=5000)       
    name = models.CharField(max_length=90)  # Lowercase & Cleaned
    email = models.CharField(max_length=90)
    address1 = models.CharField(max_length=200) # 'address1' matches checkout.html name attribute
    address2 = models.CharField(max_length=200, default="") # FIXED: Removed () parentheses error
    city = models.CharField(max_length=90)
    state = models.CharField(max_length=90)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, default="")
    amount = models.IntegerField(default=0)
    razorpay_order_id = models.CharField(max_length=100, default="", blank=True)
    razorpay_payment_id = models.CharField(max_length=100, default="", blank=True)
    razorpay_signature = models.CharField(max_length=200, default="", blank=True)
    payment_status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"Order {self.order_id} by {self.name}"
    
class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)  
    order_id = models.IntegerField(default=" ")  
    update_desc = models.CharField(max_length=5000)  
    timestamp = models.DateField(auto_now_add=True)  

    def __str__(self):
        return self.update_desc[0:7] + "..."