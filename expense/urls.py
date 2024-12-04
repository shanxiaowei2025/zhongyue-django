from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_expense_list, name='get_expense_list'),
    path('create', views.create_expense, name='create_expense'),
    path('update', views.update_expense, name='update_expense'),
    path('delete', views.delete_expense, name='delete_expense'),
    path('audit', views.audit_expense, name='audit_expense'),
    path('cancel-audit', views.cancel_audit_expense, name='cancel_audit_expense'),
    path('export', views.export_expenses, name='export_expenses'),
    path('autocomplete/', views.get_autocomplete_options, name='expense-autocomplete'),
]
