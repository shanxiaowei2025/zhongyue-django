"""
URL configuration for zhongyue_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import (
    LoginView, 
    RefreshTokenView, 
    get_async_routes, 
    get_user_list, 
    get_role_ids,
    create_user,  # 新增
    update_user,  # 新增
    delete_user,   # 新增
    reset_password,
    upload_avatar,
    get_role_list,
    get_all_roles,
    update_user_roles,  # 新增
    create_role,  # 新增
    update_role,  # 新增
    delete_role,
    get_dept_list,
    create_dept,
    update_dept,
    delete_dept,
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('get-async-routes/', get_async_routes, name='get_async_routes'),
    path('user', get_user_list, name='get_user_list'),
    path('list-role-ids', get_role_ids, name='get_role_ids'),
    path('user/create', create_user, name='create_user'),  # 新增
    path('user/update', update_user, name='update_user'),  # 新增
    path('user/delete', delete_user, name='delete_user'),  # 新增
    path('user/reset-password', reset_password, name='reset_password'),
    path('user/upload-avatar', upload_avatar, name='upload_avatar'),
    path('role', get_role_list, name='get_role_list'),  # 新增
    path('list-all-role', get_all_roles, name='get_all_roles'),  # 新增
    path('user/update-roles', update_user_roles, name='update_user_roles'),  # 新增
    path('role/create', create_role, name='create_role'),  # 新增
    path('role/update', update_role, name='update_role'),  # 新增
    path('role/delete', delete_role, name='delete_role'),  # 新增
    path('dept', get_dept_list, name='get_dept_list'),  # 新增
    path('dept/create', create_dept, name='create_dept'),  # 新增
    path('dept/update', update_dept, name='update_dept'),  # 新增
    path('dept/delete', delete_dept, name='delete_dept'),  # 新增
    path('expense/', include('expense.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
