from django.urls import path
from . import views

urlpatterns = [
    # path('',views.Register,name="register"),
    path('admin_dashboard/',views.Dashboard,name="dashboard"),
       
]