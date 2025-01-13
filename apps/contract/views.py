from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Contract
from .serializers import ContractSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contract_list(request):
    """获取合同列表"""
    queryset = Contract.objects.all()
    
    # 企业名称搜索
    company_name = request.query_params.get('company_name', None)
    if company_name:
        queryset = queryset.filter(company_name__icontains=company_name)
    
    # 合同类型筛选
    contract_type = request.query_params.get('contract_type', None)
    if contract_type:
        queryset = queryset.filter(contract_type=contract_type)
        
    # 业务类型筛选
    business_type = request.query_params.get('business_type', None)
    if business_type:
        queryset = queryset.filter(business_type=business_type)
    
    # 日期范围筛选
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    if start_date and end_date:
        queryset = queryset.filter(
            Q(start_date__gte=start_date) &
            Q(end_date__lte=end_date)
        )
    
    # 合同状态筛选
    contract_status = request.query_params.get('contract_status', None)
    if contract_status:
        queryset = queryset.filter(contract_status=contract_status)
    
    serializer = ContractSerializer(queryset, many=True)
    return Response({
        'success': True,
        'data': serializer.data
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