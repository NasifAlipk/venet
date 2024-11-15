from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"
        
        
        
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
        
        
        

class Add_product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    image1 = models.ImageField(upload_to='admin_img/')
    image2 = models.ImageField(upload_to='admin_img/', blank=True, null=True)
    image3 = models.ImageField(upload_to='admin_img/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True)
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True) 
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Add_product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.price



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.street_address}, {self.city}"

    class Meta:
        verbose_name_plural = "Addresses"
        

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username
        
class Order(models.Model):
    # Choices for payment method and status
    PAYMENT_METHOD_CHOICES = (
        ('cash on delivery', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
        ('paypal', 'PayPal'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)  # Change this line
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add discount field
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Store payment ID from Razorpay/PayPal
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    
    
    

class OrderItem(models.Model):
    STATUS_CHOICES = (
        ('purchased', 'Purchased'),
        ('returned', 'Returned'),
    )

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Add_product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='purchased')

    def __str__(self):
        return f"{self.product.title} - {self.quantity} pcs"

    @property
    def total(self):
        return self.quantity * self.price

    
    
    

class OrderStatus(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order.id} - {self.get_status_display()}"
    
    
class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7)  # HEX code

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Add_product, related_name='variants', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.title} - {self.size} - {self.color}"
    
    
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Add_product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
    
    
    
class Coupon(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField() 
    expiry_date = models.DateField()
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='inactive')

    def __str__(self):
        return f"{self.name} - {self.code}"
    
    
    
class Wallet(models.Model):
    """
    Wallet model to store user's current balance.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user has one wallet
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Wallet balance

    def __str__(self):
        return f"Wallet of {self.user.username} - Balance: RS {self.balance}"

    def credit(self, amount):
        """
        Method to credit the wallet (increase balance).
        """
        self.balance += amount
        self.save()
        return self.balance

    def debit(self, amount):
        """
        Method to debit the wallet (decrease balance), ensuring enough balance is available.
        """
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return self.balance
        else:
            raise ValueError(f"Insufficient balance in {self.user.username}'s wallet to complete this transaction.")
        


class Transaction(models.Model):
    """
    A model to track all wallet transactions (credit and debit).
    """
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)  # Wallet relationship
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically track when the transaction occurred
    description = models.TextField()  # Description of the transaction
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)  # Either 'credit' or 'debit'
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Transaction amount

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - RS {self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    
    
    
class Offer(models.Model):
    # Choices for the type of offer
    OFFER_TYPE_CHOICES = (
        ('product', 'Product'),
        ('category', 'Category'),
    )

    # Choices for the status of the offer
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    )

    name = models.CharField(max_length=200)  # Name of the offer
    description = models.TextField(blank=True)  # Detailed description of the offer
    discount_percentage = models.PositiveIntegerField()  # Discount in percentage
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)  # Type of offer
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')  # Status choices
    start_date = models.DateTimeField(default=timezone.now)  # When the offer becomes valid
    end_date = models.DateTimeField(null=True, blank=True)  # When the offer expires

    def __str__(self):
        return f"{self.name} ({self.offer_type}) - {self.discount_percentage}%"

class ProductOffer(models.Model):
    offer = models.ForeignKey(Offer, related_name='product_offers', on_delete=models.CASCADE)  # Link to Offer model
    product = models.ForeignKey(Add_product, related_name='offers', on_delete=models.CASCADE)  # Applicable product

    def __str__(self):
        return f"{self.offer.name} - {self.product.title}"

class CategoryOffer(models.Model):
    offer = models.ForeignKey(Offer, related_name='category_offers', on_delete=models.CASCADE)  # Link to Offer model
    category = models.ForeignKey(Category, related_name='offers', on_delete=models.CASCADE)  # Applicable category

    def __str__(self):
        return f"{self.offer.name} - {self.category.title}"
