from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_expense_list, name='get_expense_list'),
    path('create', views.create_expense, name='create_expense'),
    path('update', views.update_expense, name='update_expense'),
    path('delete', views.delete_expense, name='delete_expense'),
    path('company-names', views.get_company_names, name='get_company_names'),
    path('submitters', views.get_submitters, name='get_submitters'),
]
