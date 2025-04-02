from django.urls import path # type: ignore
from . import views

app_name = 'users'

urlpatterns = [
    # 登录认证
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh-token/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('get-async-routes/', views.get_async_routes, name='get_async_routes'),
    
    # 用户管理
    path('user', views.get_user_list, name='get_user_list'),
    path('list-role-ids', views.get_role_ids, name='get_role_ids'),
    path('user/create', views.create_user, name='create_user'),
    path('user/update', views.update_user, name='update_user'),
    path('user/delete', views.delete_user, name='delete_user'),
    path('user/reset-password', views.reset_password, name='reset_password'),
    path('user/upload-avatar', views.upload_avatar, name='upload_avatar'),
    path('user-roles', views.get_user_roles, name='get_user_roles'),
    path('user/update-roles', views.update_user_roles, name='update_user_roles'),
    
    # 角色管理
    path('role', views.get_role_list, name='get_role_list'),
    path('list-all-role', views.get_all_roles, name='get_all_roles'),
    path('role/create', views.create_role, name='create_role'),
    path('role/update', views.update_role, name='update_role'),
    path('role/delete', views.delete_role, name='delete_role'),
    
    # 部门管理
    path('dept', views.get_dept_list, name='get_dept_list'),
    path('dept/create', views.create_dept, name='create_dept'),
    path('dept/update', views.update_dept, name='update_dept'),
    path('dept/delete', views.delete_dept, name='delete_dept'),
    
    # 权限管理
    path('permission', views.get_permissions_list, name='get_permissions_list'),
    path('permission/update', views.update_permission, name='update_permission'),
    path('current-user-permissions/', views.get_current_user_permissions, name='current_user_permissions'),
] 