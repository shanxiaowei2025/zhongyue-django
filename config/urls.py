"""
URL configuration for zhongyue_django project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # 用户相关路由（包含了所有用户、角色、部门、权限相关的路由）
    path('', include('apps.users.urls')),
    
    # 费用管理路由
    path('expense/', include('apps.expense.urls')),
    
    # 客户管理路由
    path('customer/', include('apps.customer.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
