from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.get_customer_list, name='customer-list'),
    path('create/', views.create_customer, name='create-customer'),
    path('update/<int:pk>/', views.update_customer, name='update-customer'),
    path('delete/<int:pk>/', views.delete_customer, name='delete-customer'),
    path('detail/<int:id>/', views.get_customer_detail, name='get_customer_detail'),
]

