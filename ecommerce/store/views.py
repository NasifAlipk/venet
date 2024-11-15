import json
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random 
import string
import re
from datetime import timedelta
from django.contrib.auth import logout,login
from store.models import Category,Add_product,Cart, CartItem,Brand,Address,Order,OrderItem,OrderStatus,ProductVariant, Size, Color,Profile,WishlistItem,Coupon,Wallet, Transaction,Offer,ProductOffer,CategoryOffer
from django.contrib.auth.views import LogoutView
from django import template
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from datetime import timedelta
from django.urls import reverse
from django.http import HttpResponseForbidden
from datetime import datetime, timedelta
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal
import razorpay
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from decimal import Decimal
from django.contrib.auth import update_session_auth_hash

# RAZORPAY_KEY_ID = 'rzp_test_FwwIyWbzNNAvKY'
# RAZORPAY_KEY_SECRET = 'yLIcsMzkAD8CcMlORthD0Mtj'






from django.shortcuts import render

def CartView(request):
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Fetch cart items from the database
    cart_items = cart.cartitem_set.all()
    total_cart_price = cart.total_price
    

    # Pass cart items and total cart price to the template
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price
    }

    return render(request, 'store/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Add_product, id=product_id)

    # Get the requested quantity, default to 1 if coming from the wishlist
    quantity = int(request.POST.get('quantity', 1))

    # Ensure the quantity is at least 1
    if quantity < 1:
        return redirect('product_detail', product_id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'price': product.price})

    if not created:
        # If the item already exists in the cart, check if adding more would exceed the limit
        if cart_item.quantity + quantity > 5:
            cart_item.quantity = 5  # Set the max limit
            messages.error(request, 'Maximum of 5 units allowed per product in a single order.')
        else:
            cart_item.quantity += quantity
    else:
        # For newly added items, set the quantity to either the requested amount or 5, whichever is lower
        if quantity > 5:
            cart_item.quantity = 5
            messages.error(request, 'Maximum of 5 units allowed per product in a single order.')
        else:
            cart_item.quantity = quantity

    cart_item.save()

    return redirect('CartView')




@login_required
@require_POST
def update_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        data = json.loads(request.body)
        new_quantity_str = data.get('quantity')
        
        if new_quantity_str is None:
            return JsonResponse({'success': False, 'error': 'Quantity not provided'})
        
        try:
            new_quantity = int(new_quantity_str)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity format'})
        
        if new_quantity < 1:
            return JsonResponse({'success': False, 'error': 'Invalid quantity', 'current_quantity': cart_item.quantity})
        
        if new_quantity > cart_item.product.stock:
            return JsonResponse({'success': False, 'error': 'Not enough stock', 'current_quantity': cart_item.quantity})
        
        # Calculate the change in quantity
        quantity_change = new_quantity - cart_item.quantity
        
        # Update cart item quantity
        cart_item.quantity = new_quantity
        cart_item.save()
        
        # Update product stock
        cart_item.product.stock -= quantity_change
        cart_item.product.save()
        
        # Calculate new totals
        new_item_total = cart_item.total_price
        cart_total = cart_item.cart.total_price
        
        return JsonResponse({
            'success': True,
            'new_total': float(new_item_total),  # Convert Decimal to float for JSON serialization
            'cart_total': float(cart_total)  # Convert Decimal to float for JSON serialization
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart item not found'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})





register = template.Library()

@register.filter
def sum_total_price(cart_items):
    print("Filter called with:", cart_items)
    return sum(item['total_price'] for item in cart_items if 'total_price' in item)


def remove_from_cart(request, product_id):
    # Get the user's cart
    cart = Cart.objects.get(user=request.user)
    
    # Try to get the cart item to remove
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    
    # Remove the item from the cart
    cart_item.delete()

    # Update the cart's total price after removing the item
    cart.save()

    # Redirect back to the cart view after removal
    return redirect('CartView')  # Ensure 'cart' matches the name in urls.py


def Withouthome(request):
    return render(request,'store/without_home.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        errors = {}

        if not username:
            errors['username'] = "Username is required."
        if not password:
            errors['password'] = "Password is required."

        if not errors:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('home')
            else:
                errors['invalid'] = "Invalid username or password."

        for field, error_message in errors.items():
            messages.error(request, error_message)

    return render(request, 'store/login.html')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        # Redirect to the user-side login page after password reset completion
        return redirect(reverse_lazy('login'))
    
    


def Home(request):
    products = Add_product.objects.all()

    # Fetch the first 2 cart items for the user (assuming user is authenticated)
    cart_items = CartItem.objects.filter(cart__user=request.user)[:2] if request.user.is_authenticated else []
    
    # Calculate the total price of the cart items
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/home.html', context)




def Product_details(request, product_id):
    # Fetch the product or return a 404 error if not found
    product = get_object_or_404(Add_product, id=product_id)
    
    # Calculate the discounted price
    discount = None
    discounted_price = product.price

    # Check if there's an active product-specific offer
    product_offer = ProductOffer.objects.filter(product=product, offer__status='active').first()
    if product_offer:
        discount = product_offer.offer.discount_percentage
        discounted_price = product.price * (Decimal(1) - Decimal(discount) / Decimal(100))
    
    # If no product-specific offer, check for a category offer
    elif product.category:
        category_offer = CategoryOffer.objects.filter(category=product.category, offer__status='active').first()
        if category_offer:
            discount = category_offer.offer.discount_percentage
            discounted_price = product.price * (Decimal(1) - Decimal(discount) / Decimal(100))

    # Pass discount and discounted price to the template
    return render(request, 'store/product_details.html', {
        'product': product,
        'discount': discount,
        'discounted_price': discounted_price,
    })

def All_product(request):
    # Get selected category, brand, and search parameters
    selected_category_ids = request.GET.getlist('category_id[]')
    selected_brand_ids = request.GET.getlist('brand_id[]')
    search_query = request.GET.get('search', '')

    # Filter categories, brands, and products
    categories = Category.objects.filter(status=True)
    brands = Brand.objects.all()
    products = Add_product.objects.filter(status=True, category__status=True)

    # Apply category and brand filters
    filter_conditions = Q()
    if selected_category_ids:
        filter_conditions &= Q(category_id__in=selected_category_ids)
    if selected_brand_ids:
        filter_conditions &= Q(brand_id__in=selected_brand_ids)
    if search_query:
        filter_conditions &= (
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(category__title__icontains=search_query)
        )
    products = products.filter(filter_conditions)

    # Sorting
    sortby = request.GET.get('sortby', 'price')
    if sortby == 'price_low_high':
        products = products.order_by('price')
    elif sortby == 'price_high_low':
        products = products.order_by('-price')
    elif sortby == 'az':
        products = products.order_by('title')
    elif sortby == 'za':
        products = products.order_by('-title')

    # Calculate discounted price for each product
    for product in products:
        product.discount = None  # Default no discount
        product.discounted_price = product.price  # Default to regular price

        # Check if there's a product-specific offer
        product_offer = ProductOffer.objects.filter(product=product, offer__status='active').first()
        if product_offer:
            product.discount = product_offer.offer.discount_percentage
            product.discounted_price = product.price * (Decimal(1) - Decimal(product.discount) / Decimal(100))

        # If no product-specific offer, check for category offer
        elif product.category:
            category_offer = CategoryOffer.objects.filter(category=product.category, offer__status='active').first()
            if category_offer:
                product.discount = category_offer.offer.discount_percentage
                product.discounted_price = product.price * (Decimal(1) - Decimal(product.discount) / Decimal(100))

    # Render template with calculated discounts
    return render(request, 'store/all_product.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category_ids': selected_category_ids,
        'selected_brand_ids': selected_brand_ids,
        'search_query': search_query,
        'sortby': sortby,
    })


@login_required
def Wishlist(request):
    # Get the user's wishlist items
    wishlist_items = WishlistItem.objects.select_related('product').filter(user=request.user)
    
    # Get the user's cart and cart items
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    # Create a dictionary to hold product IDs and their quantities in the cart
    cart_quantities = {item.product.id: item.quantity for item in cart_items}

    # Calculate discounted prices for wishlist items
    for item in wishlist_items:
        product = item.product
        discounted_price = product.price  # Default to original price
        
        # Apply discount if the product has an active offer
        if hasattr(product, 'offers') and product.offers.exists():
            product_offer = product.offers.filter(offer__status='active').first()
            if product_offer:
                discount_percentage = Decimal(product_offer.offer.discount_percentage) / 100
                discounted_price = product.price * (1 - discount_percentage)
        
        # Attach discounted price to the wishlist item
        item.discounted_price = discounted_price.quantize(Decimal('0.01'))

    # Pass wishlist items and cart quantities to the template
    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items,
        'cart_quantities': cart_quantities
    })



@login_required
def add_to_wishlist(request, product_id):
    product = Add_product.objects.get(id=product_id)  # Get product from Add_product model

    # Check if the product is already in the wishlist
    if not WishlistItem.objects.filter(user=request.user, product=product).exists():
        WishlistItem.objects.create(user=request.user, product=product)

    return redirect('wishlist')  # Redirect to the wishlist page




@login_required
def remove_from_wishlist(request, product_id):
    product = Add_product.objects.get(id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist')




def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email,otp):
    subject ='Your OTP for Registration'
    message =f'Your OTP is {otp}. It will expire in 5 minutes.'
    from_email =settings.EMAIL_HOST_USER
    recipient_list=[email]
    print(recipient_list)
    send_mail(subject,message, from_email, recipient_list)
    
    


def Register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        errors = {}

        # Validate username
        if len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters long.'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors['username'] = 'Username can only contain letters, numbers, and underscores.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username is already taken.'

        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Invalid email address.'

        # Validate password
        if len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters long.'
        elif password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        # If there are validation errors, render the form with error messages
        if errors:
            for key, error in errors.items():
                messages.error(request, error)
            context = {
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': confirm_password,
            }
            return render(request, 'store/register.html', context)

        # If no errors, proceed with user creation
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()
        
        otp = generate_otp()
        print(f"otp:{otp}")
        send_otp_email(email, otp)
        
        request.session['otp'] = otp
        request.session['otp_expiry'] = (timezone.now() + timedelta(minutes=5)).isoformat()
        request.session['user_id'] = user.id
        
        return redirect('verify_otp')
    
    return render(request, 'store/register.html', {
        'username': '',
        'email': '',
        'password': '',
        'confirm_password': ''
    })

def verify_otp(request):
    if 'otp' not in request.session or 'user_id' not in request.session:
        messages.error(request, 'Please register first.')
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        expiry_time = request.session.get('otp_expiry')

        if timezone.now().isoformat() > expiry_time:
            messages.error(request, 'OTP has expired. Please request a new one.')
        elif entered_otp == stored_otp:
            user = User.objects.get(id=request.session['user_id'])
            user.is_active = True
            user.save()
            
            # Clear OTP related session data
            del request.session['otp']
            del request.session['otp_expiry']
            del request.session['user_id']

            messages.success(request, 'OTP verified successfully. You can now login.')
            return redirect('login')
        

    return render(request, 'store/verify_otp.html')




    


def resend_otp(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please register first.')
        return redirect('register')

    user = User.objects.get(id=request.session['user_id'])
    new_otp = generate_otp()
    send_otp_email(user.email, new_otp)

    # Update OTP and its expiry time in session
    request.session['otp'] = new_otp
    request.session['otp_expiry'] = (timezone.now() + timedelta(minutes=5)).isoformat()

    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('store/verify_otp')

def logout_view(request):
    logout(request)
    return redirect("store/")

def Google(request):
    return render(request, 'store/google.html')

def Accounts(request):
    errors = {}

    # Handle form submission (POST request)
    if request.method == 'POST':
        # Get user details from the form
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        # Validate user details
        if not first_name:
            errors['first_name'] = "First name is required."
        elif len(first_name) < 3:
            errors['first_name'] = "First name must be at least 3 characters long."
        elif any(char.isdigit() for char in first_name):
            errors['first_name'] = "First name cannot contain numbers."

        if not last_name:
            errors['last_name'] = "Last name is required."
        elif len(last_name) < 3:
            errors['last_name'] = "Last name must be at least 3 characters long."
        elif any(char.isdigit() for char in last_name):
            errors['last_name'] = "Last name cannot contain numbers."

        if not phone:
            errors['phone'] = "Phone number is required."
        elif not re.match(r'^[0-9]{10}$', phone):  # Validates 10 digit phone number
            errors['phone'] = "Phone number must be 10 digits."

        if not email:
            errors['email'] = "Email address is required."
        elif not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            errors['email'] = "Please enter a valid email address."

        # Handle address details
        street_address = request.POST.get('street_address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        address_phone = request.POST.get('phone', '').strip()

        # Validate address details
        if not street_address:
            errors['street_address'] = "Street address is required."
        if not city:
            errors['city'] = "City is required."
        if not state:
            errors['state'] = "State is required."
        if not postcode:
            errors['postcode'] = "Postcode is required."
        elif len(postcode) != 6 or not postcode.isdigit():
            errors['postcode'] = "Postcode must be exactly 6 digits."

        # If there are no validation errors, save the data
        if not errors:
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()

            if street_address or city or state or postcode or address_phone:
                address = Address(
                    user=user,
                    street_address=street_address,
                    city=city,
                    state=state,
                    postcode=postcode,
                    first_name=first_name,
                    last_name=last_name,
                    phone=address_phone,
                    email=email,
                )
                address.save()

            current_password = request.POST.get('current_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_new_password = request.POST.get('confirm_new_password', '').strip()

            if current_password and new_password and confirm_new_password:
                if not user.check_password(current_password):
                    messages.error(request, "Current password is incorrect.")
                elif new_password != confirm_new_password:
                    messages.error(request, "New password and confirm new password do not match.")
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Password successfully updated.")
            elif current_password or new_password or confirm_new_password:
                messages.error(request, "Please fill out all password fields to update the password.")

            return redirect('accounts')

        else:
            # Render the form with errors if validation fails
            profile, created = Profile.objects.get_or_create(user=request.user)
            addresses = Address.objects.filter(user=request.user)
            context = {
                'user': request.user,
                'profile': profile,
                'addresses': addresses,
                'errors': errors,
            }
            return render(request, 'store/accounts.html', context)

    else:
        # For GET request, load the form with existing data
        profile, created = Profile.objects.get_or_create(user=request.user)
        addresses = Address.objects.filter(user=request.user)
        context = {
            'user': request.user,
            'profile': profile,
            'addresses': addresses,
            'errors': errors,
        }
        return render(request, 'store/accounts.html', context)



    
def delete_address(request, address_id):
    if request.method == "POST":
        address = get_object_or_404(Address, id=address_id)
        address.delete()
        return redirect('accounts')  # Redirect to the address list or wherever appropriate
    
    
def edit_address(request):
    if request.method == "POST":
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id)
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.street_address = request.POST.get('street_address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postcode = request.POST.get('postcode')
        address.phone = request.POST.get('phone')
        address.email = request.POST.get('email')
        address.save()
        return redirect('accounts')  # Redirect to the checkout page or wherever needed
    return redirect('accounts')  # Handle GET or other methods




def wallet(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-timestamp')  # Use 'timestamp' instead of 'date'

    context = {
        'wallet_balance': wallet.balance,
        'transactions': transactions,
    }
    return render(request, 'store/wallet.html', context)






# Initialize Razorpay client with your provided API keys
# razorpay_client = razorpay.Client(auth=('rzp_test_FwwIyWbzNNAvKY', 'yLIcsMzkAD8CcMlORthD0Mtj'))

def Checkoutt(request):
    # Get the user's cart and items
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_cart_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in cart_items)

    addresses = Address.objects.filter(user=request.user)
    discount_amount = Decimal(0)  # Default discount amount
    applied_coupon = None
    coupons = Coupon.objects.filter(status='active')  # Retrieve all active coupons

    # Check if a coupon code was applied or removed via POST
    if request.method == 'POST':
        # Handle coupon removal
        if 'remove_coupon' in request.POST:
            if 'applied_coupon' in request.session:
                del request.session['applied_coupon']
            messages.success(request, 'Coupon removed successfully.')
            return redirect('checkoutt')

        # Handle coupon application
        coupon_code = request.POST.get('couponCode')
        if coupon_code:
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code, status='active')
                if total_cart_price < applied_coupon.minimum_amount:
                    messages.error(request, f'This coupon requires a minimum cart amount of ₹{applied_coupon.minimum_amount}.')
                    discount_amount = Decimal(0)
                    applied_coupon = None
                else:
                    discount_percentage = applied_coupon.discount_percentage
                    discount_amount = (Decimal(discount_percentage) / Decimal(100)) * total_cart_price
                    request.session['applied_coupon'] = applied_coupon.code
                    messages.success(request, f'Coupon "{applied_coupon.code}" applied successfully!')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code.')
                discount_amount = Decimal(0)

    # Check if a coupon is already in the session
    elif 'applied_coupon' in request.session:
        try:
            applied_coupon = Coupon.objects.get(code=request.session['applied_coupon'], status='active')
            discount_percentage = applied_coupon.discount_percentage
            discount_amount = (Decimal(discount_percentage) / Decimal(100)) * total_cart_price
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']

    # Calculate the final total after applying the discount
    final_total_amount = total_cart_price - discount_amount

    # If the user proceeds with placing the order
    if request.method == 'POST' and 'place_order' in request.POST:
        selected_address_id = request.POST.get('selected_address')
        selected_payment_method = request.POST.get('payment')

        if selected_address_id and selected_payment_method:
            # Wallet payment method
            if selected_payment_method == 'wallet':
                 # Get the user's wallet balance
                wallet, created = Wallet.objects.get_or_create(user=request.user)

                if wallet.balance >= final_total_amount:
                    # Debit the wallet balance
                    wallet.debit(final_total_amount)

                    # Create the order first, so we can reference it in the transaction description
                    order = Order.objects.create(
                        user=request.user,
                        address_id=selected_address_id,
                        total_amount=final_total_amount,
                        payment_method=selected_payment_method,
                        payment_status='paid',
                        delivery_date=timezone.now() + timezone.timedelta(days=7)
                    )

                    # Now we can set the transaction description, referencing the created order
                    transaction_description = f"Payment for order {order.id}"
                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='debit',
                        amount=final_total_amount,
                        description=transaction_description
                    )

                    # Add items to the order
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        )

                    # Clear the cart
                    cart.cartitem_set.all().delete()

                    request.session['order_id'] = order.id
                    messages.success(request, "Order placed successfully!")
                    return redirect('order_summery')
                else:
                    # Insufficient balance in wallet
                    messages.error(request, "Insufficient balance in wallet to complete the order.")

            elif selected_payment_method == 'cash on delivery' and final_total_amount > 1000:
                messages.error(request, "Cash on Delivery is not available for orders above ₹1000.")
                return redirect('checkoutt')

            else:
                # Handle online payment (e.g., Razorpay logic as previously)
                razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                try:
                    razorpay_order = razorpay_client.order.create({
                        "amount": int(final_total_amount * 100),
                        "currency": "INR",
                        "payment_capture": "1"
                    })
                except Exception as e:
                    messages.error(request, "Failed to create Razorpay order. Please try again.")
                    return redirect('checkoutt')

                request.session['razorpay_order_id'] = razorpay_order['id']
                request.session['selected_address_id'] = selected_address_id
                request.session['total_cart_price'] = str(final_total_amount)

                return render(request, 'store/checkoutt.html', {
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key_id': 'rzp_test_FwwIyWbzNNAvKY',
                    'total_amount': final_total_amount,
                    'user_email': request.user.email,
                    'user_name': f"{request.user.first_name} {request.user.last_name}",
                    'cart_items': cart_items,
                    'total_cart_price': total_cart_price,
                    'discount_amount': discount_amount,
                    'addresses': addresses,
                    'coupons': coupons,
                })

    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
        'discount_amount': discount_amount,
        'final_total_amount': final_total_amount,
        'addresses': addresses,
        'coupons': coupons,
        'applied_coupon': applied_coupon,  # Pass applied coupon to the template
    }

    return render(request, 'store/checkoutt.html', context)







def verify_payment(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Create a Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            # This will throw an error if verification fails
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Payment verification successful
            selected_address_id = request.session.get('selected_address_id')
            total_cart_price = Decimal(request.session.get('total_cart_price'))
            
            # Create the order after successful payment
            order = Order.objects.create(
                user=request.user,
                address_id=selected_address_id,
                total_amount=total_cart_price,
                payment_method='razorpay',  # Payment via Razorpay
                payment_status='completed', # Mark the payment as completed
                payment_id=payment_id,      # Store the Razorpay payment ID
                delivery_date=timezone.now() + timezone.timedelta(days=7)
            )

            # Move cart items to order items
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.cartitem_set.all()
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            # Clear the cart
            cart.cartitem_set.all().delete()

            # **Store the newly created order ID in session**
            request.session['order_id'] = order.id  # <--- Important

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            # Verification failed
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})







# def remove_address_from_checkout(request, address_id):
#     # Get the address object, ensure the user owns the address
#     address = get_object_or_404(Address, id=address_id, user=request.user)

#     if request.method == 'POST':
#         # Delete the address if it belongs to the user
#         address.delete()
#         # Redirect back to the checkout page or any other page
#         return redirect('checkoutt')

#     # If not a POST request, prevent access
#     return HttpResponseForbidden()


def update_address(request):
    if request.method == "POST":
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id)
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.street_address = request.POST.get('street_address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postcode = request.POST.get('postcode')
        address.phone = request.POST.get('phone')
        address.email = request.POST.get('email')
        address.save()
        return redirect('checkout')  # Redirect to the checkout page or wherever needed
    return redirect('checkout')  # Handle GET or other methods






def add_address(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_cart_price = sum(item.product.price * item.quantity for item in cart_items)

    errors = {}

    if request.method == 'POST':
        # Extract form data and remove any extra whitespace
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        street_address = request.POST.get('street_address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        # Validation logic

        # First Name: Must contain only letters and be longer than 3 characters
        if not first_name:
            errors['first_name'] = "First name is required."
        elif len(first_name) < 3 or not first_name.isalpha():
            errors['first_name'] = "First name must be at least 3 letters and contain no numbers."

        # Last Name: Same as first name requirements
        if not last_name:
            errors['last_name'] = "Last name is required."
        elif len(last_name) < 3 or not last_name.isalpha():
            errors['last_name'] = "Last name must be at least 3 letters and contain no numbers."

        # Street Address: Basic presence check
        if not street_address:
            errors['street_address'] = "Street address is required."

        # City: Basic presence check and no numeric characters allowed
        if not city:
            errors['city'] = "City is required."
        elif any(char.isdigit() for char in city):
            errors['city'] = "City must contain only letters."

        # State: Basic presence check and no numeric characters allowed
        if not state:
            errors['state'] = "State is required."
        elif any(char.isdigit() for char in state):
            errors['state'] = "State must contain only letters."

        # Postcode: Must be exactly 6 digits
        if not postcode:
            errors['postcode'] = "Postcode is required."
        elif not re.match(r'^\d{6}$', postcode):
            errors['postcode'] = "Postcode must be exactly 6 digits."

        # Phone: Must be numeric and have 10 digits (standard phone validation)
        if not phone:
            errors['phone'] = "Phone number is required."
        elif not re.match(r'^\d{10}$', phone):
            errors['phone'] = "Phone number must be exactly 10 digits."

        # Email: Basic format check for presence of "@" symbol
        if not email:
            errors['email'] = "Email address is required."
        elif '@' not in email or '.' not in email:
            errors['email'] = "Enter a valid email address."

        # If no errors, save the new address
        if not errors:
            new_address = Address(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                street_address=street_address,
                city=city,
                state=state,
                postcode=postcode,
                phone=phone,
                email=email
            )
            new_address.save()
            # Redirect to checkout page after successful save
            return redirect('checkoutt')

    # Pass errors and other context to the template
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
        'errors': errors,  # Include errors in context
        'form_data': request.POST if request.method == 'POST' else {},
    }

    return render(request, 'store/add_address.html', context)








# THIS CODE IS WHEN THE USER SELECT THE ADDRESS AT THAT TIME THAT ADDRESS ONLY SHOW IN THERE
def Order_summery(request):
    # Fetch the order ID from session
    order_id = request.session.get('order_id')

    # Ensure there is an order ID in the session
    if not order_id:
        return redirect('CartView')  # Redirect to cart if no order in session

    # Fetch the order using the ID from the session
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Calculate the total cart price
    total_cart_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in order.items.all())

    # Handle discount calculation if any
    discount_amount = Decimal(0)
    coupon_code = request.session.get('applied_coupon')

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            discount_amount = (Decimal(coupon.discount_percentage) / Decimal(100)) * total_cart_price
        except Coupon.DoesNotExist:
            discount_amount = Decimal(0)

    # Calculate the final total amount after discount
    final_total_amount = total_cart_price - discount_amount

    # Ensure the discount and total amounts are saved to the order
    order.total_amount = final_total_amount
    order.save()

    # Get order items
    order_items = order.items.all()

    # Decrease product stock based on the ordered quantity
    for item in order_items:
        product = item.product
        if product.stock >= item.quantity:  # Ensure there's enough stock
            product.stock -= item.quantity  # Decrease stock
            product.save()
        else:
            # Handle insufficient stock scenario (you may redirect or show an error message)
            return redirect('CartView')  # For now, we simply redirect back to the cart

    # Get other order details such as address and payment method
    address = order.address
    payment_method = order.get_payment_method_display()

    context = {
        'order': order,
        'order_items': order_items,
        'total_cart_price': total_cart_price,
        'discount_amount': discount_amount,
        'final_total_amount': final_total_amount,
        'address': address,
        'payment_method': payment_method,  # Display the payment method in the template
    }

    return render(request, 'store/order_summery.html', context)









def Order_details(request):
    # Fetch the orders for the logged-in user, sorted by the latest order first
    orders = Order.objects.filter(user=request.user).select_related('orderstatus', 'address').prefetch_related('items').order_by('-created_at')

    for order in orders:
        # Get the total cart price for the order
        total_cart_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in order.items.all())

        # Get the coupon code if applied
        coupon_code = request.session.get('applied_coupon')
        
        # Default discount amount
        discount_amount = Decimal(0)

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                discount_amount = (Decimal(coupon.discount_percentage) / Decimal(100)) * total_cart_price
            except Coupon.DoesNotExist:
                discount_amount = Decimal(0)

        # Calculate final total amount after discount
        final_total_amount = total_cart_price - discount_amount
        
        # Store the calculated values back to order for use in the template
        order.total_cart_price = total_cart_price
        order.discount_amount = discount_amount
        order.final_total_amount = final_total_amount

    context = {
        'orders': orders,  # Pass the orders including the discount amounts to the template
    }

    return render(request, 'store/order_details.html', context)





def generate_invoice(request, order_id):
    # Fetch the order by ID
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Prepare the context data to pass into the template
    context = {
        'order': order,
    }

    # Render the HTML content for the invoice
    html_string = render_to_string('store/invoice_template.html', context)

    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Generate PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response






@csrf_protect
@require_POST
def return_order(request):
    order_id = request.POST.get('order_id')
    item_id = request.POST.get('item_id')

    # Fetch the order ensuring it belongs to the current user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # If item_id is provided, process the return for the specific item
    if item_id:
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)

        # Update item status to 'Returned'
        order_item.status = 'Returned'
        order_item.save()

        # Increase stock for returned item
        product = order_item.product
        product.stock += order_item.quantity
        product.save()

        # Check if all items are returned, then mark the entire order as returned
        if all(item.status == 'Returned' for item in order.items.all()):
            order.orderstatus.status = 'Returned'
            order.orderstatus.save()

            # Handle refund to wallet
            if order.payment_method == 'razorpay':
                amount_to_credit = order.total_amount
                wallet, created = Wallet.objects.get_or_create(user=request.user)
                wallet.balance += amount_to_credit
                wallet.save()
                Transaction.objects.create(
                    wallet=wallet,
                    description=f'Credit for returned order {order.id}',
                    transaction_type='credit',
                    amount=amount_to_credit,
                )

        return JsonResponse({'success': True, 'message': 'Item returned successfully and stock updated'})

    # If no item_id is provided, mark the entire order as returned
    order.orderstatus.status = 'Returned'
    order.orderstatus.save()

    # Increase stock for all items in the order
    for item in order.items.all():
        product = item.product
        product.stock += item.quantity
        product.save()

    # Handle refund to wallet
    if order.payment_method == 'razorpay':
        amount_to_credit = order.total_amount
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount_to_credit
        wallet.save()
        Transaction.objects.create(
            wallet=wallet,
            description=f'Credit for returned order {order.id}',
            transaction_type='credit',
            amount=amount_to_credit,
        )

    return JsonResponse({'success': True, 'message': 'Order returned successfully, stock updated, and amount credited to wallet'})



@csrf_protect
@require_POST
def cancel_order(request):
    order_id = request.POST.get('order_id')
    item_id = request.POST.get('item_id')

    # Fetch the order ensuring it belongs to the current user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # If item_id is provided, cancel only that specific item
    if item_id:
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        order_item.status = 'Canceled'
        order_item.save()

        # Increase stock for canceled item
        product = order_item.product
        product.stock += order_item.quantity
        product.save()

        # Check if all items are canceled, then cancel the entire order
        if all(item.status == 'Canceled' for item in order.items.all()):
            order.orderstatus.status = 'Canceled'
            order.orderstatus.save()

            # Handle refund to wallet
            if order.payment_method == 'razorpay':
                amount_to_refund = order.total_amount
                wallet, created = Wallet.objects.get_or_create(user=request.user)
                wallet.balance += amount_to_refund
                wallet.save()
                Transaction.objects.create(
                    wallet=wallet,
                    description=f'Refund for canceled order {order.id}',
                    transaction_type='credit',
                    amount=amount_to_refund,
                )

        return JsonResponse({'success': True, 'message': 'Item canceled successfully and stock updated'})

    # If no item_id is provided, cancel the entire order
    order.orderstatus.status = 'Canceled'
    order.orderstatus.save()

    # Increase stock for all items in the order
    for item in order.items.all():
        product = item.product
        product.stock += item.quantity
        product.save()

    # Handle refund to wallet
    if order.payment_method == 'razorpay':
        amount_to_refund = order.total_amount
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount_to_refund
        wallet.save()
        Transaction.objects.create(
            wallet=wallet,
            description=f'Refund for canceled order {order.id}',
            transaction_type='credit',
            amount=amount_to_refund,
        )

    return JsonResponse({'success': True, 'message': 'Order canceled successfully, stock updated, and amount refunded to wallet'})








@receiver(post_save, sender=Order)
def create_order_status(sender, instance, created, **kwargs):
    if created:
        OrderStatus.objects.create(order=instance)


def custom_404(request, exception):
    return render(request, 'store/404.html', status=404)

def custom_500(request):
    return render(request, 'store/500.html', status=500)