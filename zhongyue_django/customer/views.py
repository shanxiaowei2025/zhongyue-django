from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.paginator import Paginator
from .models import Customer
from .serializers import CustomerSerializer
from .permissions import get_user_permissions
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
import os
from django.conf import settings
import json
from pathlib import Path
import uuid
from django.utils.encoding import escape_uri_path
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation

# Create your views here.

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all().order_by('-id')
    serializer_class = CustomerSerializer
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

def apply_permission_filters(queryset, user):
    user_permissions = get_user_permissions(user)
    
    if not user_permissions['data']['viewAll']:
        filters = Q()
        
        if user_permissions['data']['viewOwn']:
            filters |= Q(submitter=user.username)
        
        if user_permissions['data']['viewByLocation']:
            filters |= Q(business_address__icontains=user_permissions['data']['viewByLocation'])
        
        if user_permissions['data']['viewDepartmentSubmissions']:
            department_users = User.objects.filter(dept_id=user.dept_id).values_list('username', flat=True)
            filters |= Q(submitter__in=department_users)
        
        queryset = queryset.filter(filters)
    
    return queryset, user_permissions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_list(request):
    user = request.user
    
    queryset = Customer.objects.all()
    queryset, user_permissions = apply_permission_filters(queryset, user)
    
    # 获取查询参数
    company_name = request.query_params.get('companyName')
    enterprise_status = request.query_params.get('enterpriseStatus')
    submitter = request.query_params.get('submitter')
    establishment_date_start = request.query_params.get('establishmentDateStart')
    establishment_date_end = request.query_params.get('establishmentDateEnd')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))

    # 应用搜索过滤
    if company_name:
        queryset = queryset.filter(company_name__icontains=company_name)
    if enterprise_status:
        queryset = queryset.filter(enterprise_status=enterprise_status)
    if submitter:
        queryset = queryset.filter(submitter__icontains=submitter)
    if establishment_date_start and establishment_date_end:
        queryset = queryset.filter(establishment_date__range=[establishment_date_start, establishment_date_end])

    # 排序
    queryset = queryset.order_by('-id')

    # 分页
    paginator = Paginator(queryset, page_size)
    customers = paginator.get_page(page)

    serializer = CustomerSerializer(customers, many=True, context={'request': request})
    return Response({
        'success': True,
        'data': {
            'list': serializer.data,
            'total': paginator.count,
            'currentPage': page,
            'pageSize': page_size,
            'permissions': user_permissions
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_customer(request):
    data = request.data.copy()
    image_fields = ['legal_person_id_images', 'other_id_images', 'business_license_images', 'bank_account_license_images', 'supplementary_images']
    
    for field in image_fields:
        files = request.FILES.getlist(field)
        saved_paths = []
        
        for file in files:
            saved_path = save_image(file, request)
            saved_paths.append(saved_path)
        
        data[field] = json.dumps(saved_paths)

    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        serializer.save(submitter=request.user.username)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def save_image(image, request):
    # 生成一个唯一的文件名，避免中文和特殊字符问题
    file_extension = Path(image.name).suffix
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    
    file_path = Path(settings.MEDIA_ROOT) / 'customer_images' / unique_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open('wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    
    relative_url = str(Path(settings.MEDIA_URL) / 'customer_images' / unique_filename).replace('\\', '/')
    
    # 使用 escape_uri_path 来确保 URL 是正确编码的
    escaped_relative_url = escape_uri_path(relative_url)
    full_url = request.build_absolute_uri(escaped_relative_url)
    
    return full_url

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_customer(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({'success': False, 'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    print(data)
    image_fields = ['legal_person_id_images', 'other_id_images', 'business_license_images', 'bank_account_license_images', 'supplementary_images']
    
    # 处理 'null' 字符串和特殊字段
    for key, value in data.items():
        if value == 'null':
            data[key] = None
        elif key in ['has_online_banking', 'is_online_banking_custodian']:
            data[key] = value.lower() == 'true' if value is not None else None
        elif key in ['registered_capital', 'paid_in_capital']:
            try:
                data[key] = Decimal(value) if value not in [None, ''] else None
            except InvalidOperation:
                data[key] = None

    # 移除 item_permissions 字段，因为它不是客户模型的一部分
    data.pop('item_permissions', None)

    for field in image_fields:
        files = request.FILES.getlist(field)
        existing_images = getattr(customer, field)
        
        if isinstance(existing_images, str):
            try:
                existing_images = json.loads(existing_images)
            except json.JSONDecodeError:
                existing_images = []
        elif not isinstance(existing_images, list):
            existing_images = []

        new_images = []
        
        for file in files:
            saved_path = save_image(file, request)
            new_images.append(saved_path)
        
        # 如果没有新上传的文件，保留现有的图片
        if not new_images and field in data:
            try:
                data[field] = json.loads(data[field])
            except json.JSONDecodeError:
                data[field] = existing_images
        else:
            # 合并现有的图片和新上传的图片
            updated_images = existing_images + new_images
            data[field] = updated_images

    try:
        serializer = CustomerSerializer(customer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response({'success': False, 'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({'success': False, 'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    customer.delete()
    return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)

def save_images(images):
    image_urls = []
    for image in images:
        file_path = os.path.join(settings.MEDIA_ROOT, 'customer_images', image.name)
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        image_urls.append(os.path.join(settings.MEDIA_URL, 'customer_images', image.name))
    return image_urls




