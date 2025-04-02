"""
URL configuration for zhongyue_django project.
"""
from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore # type: ignore
from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # 用户相关路由（包含了所有用户、角色、部门、权限相关的路由）
    path('', include('apps.users.urls')),
    
    # 费用管理路由
    path('expense/', include('apps.expense.urls')),
    
    # 客户管理路由
    path('customer/', include('apps.customer.urls')),
    
    # 文件上传路由
    path('fileupload/', include('apps.fileupload.urls')),
    
    # 合同管理路由
    path('contract/', include('apps.contract.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
