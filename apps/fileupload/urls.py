from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.get_presigned_url, name='get-presigned-url'),
]