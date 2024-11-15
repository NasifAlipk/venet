from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import CustomPasswordResetCompleteView




urlpatterns = [
    path('',views.Withouthome,name="withouthome"),
    path('register/',views.Register,name="register"),
    path('google/', views.Google, name='google'),
    path('login/',views.Login,name="login"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='store/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='store/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='store/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='store/password_reset_complete.html'),name='password_reset_complete'),
    path('home/',views.Home,name="home"),
    path("product_details/<int:product_id>/",views.Product_details,name="product_details"),
    path('all_product/',views.All_product,name='all_product'),
    path("logout",views.logout_view),
    path('verify_otp/',views.verify_otp,name="verify_otp"),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('cart/', views.CartView, name='CartView'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item/<int:item_id>/', views.update_cart_item,name="update_cart_item"),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('account/',views.Accounts,name="accounts"),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('edit_address/', views.edit_address, name='edit_address'),
    # path('edit-address/<int:address_id>/', views.EditAddress, name='edit_address'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('checkoutt/', views.Checkoutt, name='checkoutt'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    # path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    # path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    # path('remove_address_from_checkout/<int:address_id>/', views.remove_address_from_checkout, name='remove_address_from_checkout'),
    path('update_address/', views.update_address, name='update_address'),
    path('add_address/', views.add_address, name='add_address'),
    path('order-summery/', views.Order_summery, name='order_summery'),
    path('order-details/', views.Order_details, name='order_details'),
    path('order/<int:order_id>/invoice/', views.generate_invoice, name='generate_invoice'),
    path('return_order/', views.return_order, name='return_order'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('wishlist/', views.Wishlist, name='wishlist'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wallet/',views.wallet,name="wallet"),
    
]