from django.urls import path
from . import views
from .views import toggle_user_status
from .views import toggle_category_status

urlpatterns = [
    path('login/',views.Admin_login,name="admin_login"),
    path('dashboard/',views.Dashboard,name="dashboard"),
    path('product_list/',views.Product_list,name="product_list"),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('add_product/',views.Add_Product,name="add_product"),
    path('category_list/',views.Category_list,name="category_list"),
    path('edit-category/', views.edit_category, name='edit_category'),
    path('all_customer/',views.All_customer,name="all_customer"),
    path('user/toggle_status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('toggle-category-status/', toggle_category_status, name='toggle_category_status'),
    path('toggle-status/<int:product_id>/', views.toggle_product_status, name='toggle_product_status'),
    path('order_list/',views.Order_list,name="order_list"),
    path('admin/confirm-return/', views.confirm_return, name='confirm_return'),
    path('coupon/',views.coupon,name="coupon"),
    path('coupon/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    path('sales_report/',views.sales_report,name="sales_report"),
    path('export_sales_report_pdf/', views.export_sales_report_pdf, name='export_sales_report_pdf'),
    path('export_sales_report_excel/', views.export_sales_report_excel, name='export_sales_report_excel'),  # Add this line
    path('offer/', views.offer, name='offer'),
    path('offer/add_category/', views.add_category_offer, name='add_category_offer'),
    path('offers/delete/<int:offer_id>/', views.delete_category_offer, name='delete_category_offer'),
    path('add-product-offer/', views.add_product_offer, name='add_product_offer'),
    path('delete-product-offer/<int:pk>/', views.delete_product_offer, name='delete_product_offer'),

]