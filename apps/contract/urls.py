from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.contract_list, name='contract_list'),  # 获取合同列表
    path('create/', views.create_contract, name='create_contract'),  # 创建合同
    path('update/<int:pk>/', views.update_contract, name='update_contract'),  # 更新合同
    path('delete/<int:pk>/', views.delete_contract, name='delete_contract'),  # 删除合同
] 