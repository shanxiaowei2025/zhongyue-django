from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Contract
from .serializers import ContractSerializer
from apps.users.views import get_user_permissions_helper

def apply_permission_filters(queryset, user):
    """
    根据用户权限过滤合同数据
    """
    user_permissions = get_user_permissions_helper(user)
    contract_permissions = user_permissions['permissions']['contract']
    
    if not contract_permissions['data']['view_all']:
        filters = Q()
        
        if contract_permissions['data']['view_own']:
            filters |= Q(submitter=user.nickname)
        
        if contract_permissions['data']['view_by_location']:
            # 假设合同表中有 business_location 字段，根据实际情况调整
            filters |= Q(business_location__icontains=user.location)
        
        if contract_permissions['data']['view_department_submissions']:
            department_users = user.objects.filter(dept_id=user.dept_id).values_list('username', flat=True)
            filters |= Q(submitter__in=department_users)
        
        queryset = queryset.filter(filters)
    
    return queryset, contract_permissions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contract_list(request):
    """获取合同列表"""
    queryset = Contract.objects.all()
    
    # 应用权限过滤
    queryset, contract_permissions = apply_permission_filters(queryset, request.user)
    
    # 合同编号搜索
    contract_no = request.query_params.get('contract_no', None)
    if contract_no:
        queryset = queryset.filter(contract_no__icontains=contract_no)
    
    # 客户名称搜索
    customer_name = request.query_params.get('customer_name', None)
    if customer_name:
        queryset = queryset.filter(customer_name__icontains=customer_name)
        
    # 业务类型筛选
    business_type = request.query_params.get('business_type', None)
    if business_type:
        queryset = queryset.filter(business_type=business_type)
    
    # 业务人员筛选
    business_person = request.query_params.get('business_person', None)
    if business_person:
        queryset = queryset.filter(business_person__icontains=business_person)
    
    # 日期范围筛选
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    if start_date and end_date:
        queryset = queryset.filter(
            Q(sign_date__gte=start_date) &
            Q(sign_date__lte=end_date)
        )
    
    # 合同状态筛选
    status = request.query_params.get('status', None)
    if status:
        queryset = queryset.filter(status=status)
    
    # 获取分页参数
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    
    # 排序
    queryset = queryset.order_by('-id')
    
    # 分页
    paginator = Paginator(queryset, page_size)
    contracts = paginator.get_page(page)
    
    serializer = ContractSerializer(contracts, many=True)
    
    return Response({
        'success': True,
        'data': {
            'list': serializer.data,
            'total': paginator.count,
            'pageSize': page_size,
            'currentPage': page,
            'permissions': contract_permissions
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_contract(request):
    """创建合同"""
    data = request.data.copy()
    # 使用用户的昵称（如果有）或用户名
    data['submitter'] = request.user.nickname if hasattr(request.user, 'nickname') else request.user.username
    serializer = ContractSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': '合同创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': '合同创建失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_contract(request, pk):
    """更新合同"""
    try:
        contract = Contract.objects.get(pk=pk)
        data = request.data.copy()
        # 更新时不允许修改提交人
        if 'submitter' in data:
            del data['submitter']
            
        serializer = ContractSerializer(contract, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '合同更新成功',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'message': '合同更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Contract.DoesNotExist:
        return Response({
            'success': False,
            'message': '合同不存在'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_contract(request, pk):
    """删除合同"""
    try:
        contract = Contract.objects.get(pk=pk)
        contract.delete()
        return Response({
            'success': True,
            'message': '合同删除成功'
        })
    except Contract.DoesNotExist:
        return Response({
            'success': False,
            'message': '合同不存在'
        }, status=status.HTTP_404_NOT_FOUND) 