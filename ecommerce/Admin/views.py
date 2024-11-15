from django.db import IntegrityError
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store.models import Category, Add_product,Brand,Order,OrderItem,OrderStatus,Coupon,Offer,ProductOffer,CategoryOffer
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponseForbidden
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
from django.utils import timezone
from xhtml2pdf import pisa
from django.template.loader import get_template
import openpyxl
from io import BytesIO
from django.core.paginator import Paginator
from datetime import date
from datetime import timedelta



def admin_required(view_func, redirect_if_not_admin=True):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            if redirect_if_not_admin:
                return redirect(reverse('admin_login'))  # Redirect to the admin login page
            else:
                return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view



def Admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('email-username')
        password = request.POST.get('password')
        
        # Authenticate using username and password only
        admin = authenticate(request, username=username, password=password)
        
        if admin is not None and admin.is_superuser:
            login(request, admin)
            return redirect('dashboard')  # Redirect to admin dashboard
        else:
            messages.error(request, 'Invalid Admin Username or Password...!')

    return render(request, 'admin_login.html')


@admin_required
def Dashboard(request):
    # Get the selected interval from the request, default to 'all' (no filter)
    interval = request.GET.get('interval', 'all')

    # Query to fetch all orders
    orders = Order.objects.all()

    # Filter orders based on selected interval
    if interval == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
        orders = orders.filter(created_at__gte=start_date)
    elif interval == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
        orders = orders.filter(created_at__gte=start_date)
    elif interval == 'yearly':
        start_date = timezone.now() - timedelta(days=365)
        orders = orders.filter(created_at__gte=start_date)

    # Aggregate data based on filtered orders
    total_orders = orders.count()
    total_razorpay_orders = orders.filter(payment_method='razorpay', payment_status='completed').count()
    total_razorpay_sales = orders.filter(payment_method='razorpay', payment_status='completed').aggregate(total_razorpay=Sum('total_amount'))['total_razorpay'] or 0
    order_details = orders.filter(payment_status='completed').order_by('-created_at')

    # Pagination
    paginator = Paginator(order_details, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch top products, categories, brands based on filtered data
    top_products = (
        OrderItem.objects.filter(order__in=orders, order__payment_status='completed')
        .values('product__title', 'product__image1')
        .annotate(total_ordered=Count('id'))
        .order_by('-total_ordered')[:10]
    )
    top_categories = (
        OrderItem.objects.filter(order__in=orders, order__payment_status='completed')
        .values('product__category__title')
        .annotate(total_ordered=Count('id'))
        .order_by('-total_ordered')[:10]
    )
    top_brands = (
        OrderItem.objects.filter(order__in=orders, order__payment_status='completed')
        .values('product__brand__name')
        .annotate(total_ordered=Count('id'))
        .order_by('-total_ordered')[:10]
    )

    delivered_orders = orders.filter(orderstatus__status='delivered').count()
    pending_orders = orders.filter(orderstatus__status='pending').count()
    shipped_orders = orders.filter(orderstatus__status='shipped').count()

    # Pass the interval and other data to the template
    context = {
        'total_orders': total_orders,
        'total_razorpay_orders': total_razorpay_orders,
        'total_razorpay_sales': total_razorpay_sales,
        'order_details': page_obj,
        'top_products': top_products,
        'top_categories': top_categories,
        'top_brands': top_brands,
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'selected_interval': interval,  # Pass the interval to template
    }

    return render(request, 'dashboard.html', context)





def All_customer(request):
    users = User.objects.all()
    
    context = {
        'users': users
    }
    return render(request, 'all_customer.html', context)

def toggle_user_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active  # Toggle the active status
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    return redirect('all_customer')  # Replace 'your_account_page' with the actual name of your account page




def Category_list(request):
    print('catgory')
    categories = Category.objects.all()
    if request.method == 'POST':
        print('is working')
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('isListed') == 'on'  # 'on' if checked, None if unchecked
        print('hello')

        if title:
            Category.objects.create(title=title, description=description, status=status)
            messages.success(request, 'Category added successfully.')
        else:
            messages.error(request, 'Title is required.')
    context = {'categories': categories}
    
    return render(request, 'Category_list.html',context)


def toggle_category_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category_id = data.get('id')
        new_status = data.get('status')
        try:
            category = Category.objects.get(id=category_id)
            category.status = new_status
            category.save()
            return JsonResponse({'success': True})
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Category not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



def edit_category(request):
    print("helllllolo")
    
    if request.method == 'POST':
        print("helllllolo")

        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)

        # Update category details
        category.title = request.POST.get('title')
        category.description = request.POST.get('description')
        # category.status = request.POST.get('status')
        status_value = request.POST.get('status')
        category.status = True if status_value == 'true' else False

        # Save changes
        category.save()

        # Redirect back to the category list page or wherever appropriate
        return redirect('category_list')  # Replace with your view name

    # If the request is not POST, you can redirect or handle it differently
    return redirect('category_list')  # Replace with your view name



def Product_list(request):
    products = Add_product.objects.all()
    return render(request, 'product_list.html', {'products': products})




def toggle_product_status(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Add_product, id=Add_product)
        product.status = not product.status  # Toggle status
        product.save()
        return JsonResponse({'success': True, 'status': product.status})
    return JsonResponse({'success': False})


def edit_product(request, product_id):
    product = get_object_or_404(Add_product, id=product_id)

    if request.method == 'POST':
        # Get data from form
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        status = request.POST.get('status')

        # Update product details
        product.title = title
        product.description = description
        product.price = price
        product.stock = stock
        product.status = status
        product.save()

        # Redirect to product list or another page
        return redirect('product_list')  # Adjust URL name to your needs

    return render(request, 'store/edit_product.html', {'product': product})



def Add_Product(request):
    if request.method == 'POST':
        # Process the form data
        title = request.POST.get('productTitle')
        description = request.POST.get('productDescription')
        price = request.POST.get('productPrice')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        brand_name = request.POST.get('brand')  # Get the brand name from the form
        status = request.POST.get('status')

        # Handle file uploads
        image1 = request.FILES.get('productImage1')
        image2 = request.FILES.get('productImage2')
        image3 = request.FILES.get('productImage3')

        try:
            category = Category.objects.get(id=category_id)

            # Check if brand exists; if not, create a new one
            brand, created = Brand.objects.get_or_create(name=brand_name)

            product = Add_product.objects.create(
                title=title,
                description=description,
                price=price,
                stock=stock,
                category=category,
                brand=brand,  # Assign the brand instance to the product
                status=status,
                image1=image1,
                image2=image2,
                image3=image3,
            )

            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
        except Exception as e:
            print(f'Error: {str(e)}')
            messages.error(request, f'Error adding product: {str(e)}')

    # If it's a GET request or if there was an error, render the form
    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})





def Order_list(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        try:
            order_status = OrderStatus.objects.get(order_id=order_id)
            
            # If the new status is 'Confirm Return', update it to 'Returned'
            if new_status == "confirm_return":
                order_status.status = "Returned"
            else:
                order_status.status = new_status
                
            order_status.save()
            return JsonResponse({'status': 'success'})
        except OrderStatus.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order status not found'})

    # Fetch all orders for GET requests, ordering by 'id' in descending order
    orders = Order.objects.all().select_related('orderstatus', 'user').order_by('-id')

    context = {
        'orders': orders,
    }

    return render(request, 'order_list.html', context)


def confirm_return(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')

        try:
            order_status = OrderStatus.objects.get(order_id=order_id)
            if order_status.status == 'Return Requested':
                order_status.status = 'Return Confirmed'
                order_status.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid status for return confirmation.'})
        except OrderStatus.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order status not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})






@csrf_exempt
def admin_update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        try:
            # Find the order and its status
            order_status = OrderStatus.objects.get(order_id=order_id)

            # Prevent the admin from changing status to "canceled"
            if new_status == "canceled":
                return JsonResponse({'status': 'error', 'message': 'Admin cannot change the order to canceled.'})

            # Prevent updating if the order is already canceled
            if order_status.status == "canceled":
                return JsonResponse({'status': 'error', 'message': 'This order has already been canceled by the user.'})

            # Update the order status in the database
            order_status.status = new_status
            order_status.save()

            return JsonResponse({'status': 'success'})

        except OrderStatus.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order status not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




def coupon(request):
    if request.method == "POST":
        coupon_id = request.POST.get('couponId')
        name = request.POST.get('couponName')
        code = request.POST.get('couponCode')
        minimum_amount = request.POST.get('minimumAmount')
        discount_percentage = request.POST.get('redeemPercentage')
        expiry_date = request.POST.get('expiryDate')
        status = request.POST.get('status')

        # Initialize an error dictionary to track specific field errors
        errors = {}

        # Coupon name validation
        if not name or len(name) < 3:
            errors['name'] = "Coupon name must be at least 3 characters long."

        # Coupon code validation
        if not code or len(code) < 3:
            errors['code'] = "Coupon code must be at least 3 characters long."
        elif Coupon.objects.filter(code=code).exclude(id=coupon_id).exists():
            errors['code'] = "Coupon code already exists. Please use a different code."

        # Minimum amount validation
        try:
            minimum_amount = float(minimum_amount)
            if minimum_amount <= 0:
                errors['minimum_amount'] = "Minimum amount must be greater than zero."
        except ValueError:
            errors['minimum_amount'] = "Minimum amount must be a valid number."

        # Discount percentage validation
        try:
            discount_percentage = int(discount_percentage)
            if discount_percentage <= 0 or discount_percentage > 100:
                errors['discount_percentage'] = "Discount percentage must be between 1 and 100."
        except ValueError:
            errors['discount_percentage'] = "Discount percentage must be a valid number between 1 and 100."

        # Expiry date validation
        try:
            expiry_date = date.fromisoformat(expiry_date)
            if expiry_date <= date.today():
                errors['expiry_date'] = "Expiry date must be a future date."
        except ValueError:
            errors['expiry_date'] = "Invalid expiry date format."

        # If there are errors, return them in context and render the form
        if errors:
            context = {
                'coupons': Coupon.objects.all(),
                'errors': errors,
                'form_data': {
                    'name': name,
                    'code': code,
                    'minimum_amount': minimum_amount,
                    'discount_percentage': discount_percentage,
                    'expiry_date': expiry_date,
                    'status': status
                },
                'show_add_modal': True  # Flag to show the modal
            }
            return render(request, 'coupon.html', context)

        # Proceed to update or create coupon if there are no errors
        if coupon_id:
            coupon_to_edit = get_object_or_404(Coupon, id=coupon_id)
            coupon_to_edit.name = name
            coupon_to_edit.code = code
            coupon_to_edit.minimum_amount = minimum_amount
            coupon_to_edit.discount_percentage = discount_percentage
            coupon_to_edit.expiry_date = expiry_date
            coupon_to_edit.status = status
            coupon_to_edit.save()
        else:
            new_coupon = Coupon(
                name=name,
                code=code,
                minimum_amount=minimum_amount,
                discount_percentage=discount_percentage,
                expiry_date=expiry_date,
                status=status
            )
            new_coupon.save()

        return redirect('coupon')

    return render(request, 'coupon.html', {'coupons': Coupon.objects.all()})



def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)  # Get the coupon or raise a 404 error
    coupon.delete()  # Delete the coupon from the database
    messages.success(request, "Coupon deleted successfully!")  # Success message
    return redirect('coupon')  # Redirect back to the coupon management page



def sales_report(request):
    # Get the start and end dates from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Query to fetch all orders
    orders = Order.objects.all()

    # If dates are provided, filter orders by date range
    if start_date and end_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        orders = orders.filter(created_at__date__range=[start_date, end_date])

    # Total Razorpay Orders count (only for Razorpay orders)
    total_razorpay_orders = orders.filter(payment_method='razorpay', payment_status='completed').count()

    # Total Sales Amount via Razorpay (for completed Razorpay payments)
    total_razorpay_sales = orders.filter(payment_method='razorpay', payment_status='completed').aggregate(total_razorpay=Sum('total_amount'))['total_razorpay'] or 0

    # Fetch all orders for the detailed report table (filter only successful payments)
    order_details = orders.filter(payment_status='completed').order_by('-created_at')

    # Implement pagination (showing 10 orders per page)
    paginator = Paginator(order_details, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the appropriate page

    context = {
        'total_orders': total_razorpay_orders,  # Total Razorpay orders
        'total_razorpay_sales': total_razorpay_sales,  # Total amount via Razorpay
        'order_details': page_obj,  # Paginated order details
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'sales_report.html', context)



# View to generate and download PDF
def export_sales_report_pdf(request):
    # Get the start and end dates from the GET request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Initialize the date variables
    start_date = None
    end_date = None

    # If dates are provided, convert them from strings to date objects
    if start_date_str and end_date_str:
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Fetch only Razorpay orders with completed payment status
    razorpay_orders = Order.objects.filter(payment_method='razorpay', payment_status='completed')

    # If dates are provided, filter orders by date range
    if start_date and end_date:
        razorpay_orders = razorpay_orders.filter(created_at__date__range=[start_date, end_date])

    # Calculate the total sales amount for Razorpay orders
    total_razorpay_sales_amount = razorpay_orders.aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0

    # Count the total Razorpay orders
    total_razorpay_orders = razorpay_orders.count()

    # Get Razorpay order details (only completed Razorpay payments)
    order_details = razorpay_orders.order_by('-created_at')

    # Context for the template
    context = {
        'total_orders': total_razorpay_orders,  # Total Razorpay orders
        'total_sales_amount': total_razorpay_sales_amount,  # Total Razorpay sales amount
        'order_details': order_details,  # Detailed Razorpay order information
        'start_date': start_date,
        'end_date': end_date,
    }

    # Load the template and pass the context
    template_path = 'sales_report_pdf.html'
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Create PDF using xhtml2pdf pisa
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Return the PDF if successful, otherwise return an error
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the report.', status=500)
    
    return response






# View to generate and download Excel
def export_sales_report_excel(request):
    orders = Order.objects.all()
    order_details = orders.filter(payment_status='completed').order_by('-created_at')

    # Create a new workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Sales Report'

    # Define column headers
    headers = ['Order Id', 'Customer Name', 'Order Date', 'Total Amount', 'Payment Method', 'Payment Status', 'Order Status']
    sheet.append(headers)

    # Populate the sheet with order data
    for order in order_details:
        sheet.append([
            order.id,
            order.user.username,
            order.created_at.strftime('%d/%m/%Y'),
            order.total_amount,
            order.get_payment_method_display(),
            order.payment_status,
            order.orderstatus.get_status_display(),
        ])

    # Save the workbook to a BytesIO object
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    # Create the response object
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'

    return response




def offer(request):
    # Get all the category offers
    category_offers = CategoryOffer.objects.select_related('offer', 'category').all()
    product_offers = ProductOffer.objects.select_related('offer', 'product').all()
    
    # Filter active products and categories
    products = Add_product.objects.filter(status=True)
    categories = Category.objects.filter(status=True)

    return render(request, 'offer.html', {
        'categories': categories,  # For the category dropdown
        'products': products,  # For the product dropdown
        'category_offers': category_offers,  # To display existing category offers
        'product_offers': product_offers  # To display existing product offers
    })

def add_category_offer(request):
    if request.method == 'POST':
        offer_name = request.POST['offer_name']
        description = request.POST['description']
        discount_percentage = request.POST['discount_percentage']
        category_id = request.POST['category']
        status = request.POST['status']

        # Create the offer instance
        offer = Offer.objects.create(
            name=offer_name,
            description=description,
            discount_percentage=discount_percentage,
            offer_type='category',  # This is a category offer
            status=status
        )

        # Associate the offer with the selected category
        category = Category.objects.get(id=category_id)
        CategoryOffer.objects.create(offer=offer, category=category)

        # Redirect back to the offer page after adding the new category offer
        return redirect('offer')

    return redirect('offer')

def delete_category_offer(request, offer_id):
    if request.method == 'POST':
        # Retrieve the category offer by its ID
        category_offer = get_object_or_404(CategoryOffer, id=offer_id)
        
        # Delete the associated offer
        category_offer.offer.delete()
        
        # Redirect back to the offers page after deletion
        return redirect('offer')

    # If the request method is not POST, redirect to the offer page
    return redirect('offer')



def add_product_offer(request):
    if request.method == "POST":
        offer_name = request.POST['offer_name']
        discount_percentage = request.POST['discount_percentage']
        description = request.POST['description']
        product_id = request.POST['product']
        status = request.POST['status']

        # Create a new Offer object
        offer = Offer.objects.create(
            name=offer_name,
            description=description,
            discount_percentage=discount_percentage,
            offer_type='product',
            status=status
        )

        # Get the selected product
        product = Add_product.objects.get(id=product_id)

        # Create the ProductOffer entry
        ProductOffer.objects.create(
            offer=offer,
            product=product
        )

        return redirect('offer')  # Redirect back to the offers page

    return redirect('offer')


def delete_product_offer(request, pk):
    product_offer = get_object_or_404(ProductOffer, pk=pk)
    product_offer.delete()
    return redirect('offer')