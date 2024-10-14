from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
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
@parser_classes([MultiPartParser, FormParser])
def create_customer(request):
    data = request.data.copy()
    image_fields = ['legal_person_id_images', 'other_id_images', 'business_license_images', 'bank_account_license_images']
    
    for field in image_fields:
        files = request.FILES.getlist(field)
        saved_paths = []
        for file in files:
            # 生成一个唯一的文件名
            file_name = f"{field}_{file.name}"
            subdirectory = 'customer_images'
            full_path = os.path.join(settings.MEDIA_ROOT, subdirectory, file_name)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # 构建完整的 URL
            relative_url = f"{settings.MEDIA_URL}{subdirectory}/{file_name}"
            full_url = request.build_absolute_uri(relative_url)
            saved_paths.append(full_url)
        
        data[field] = saved_paths
    
    
    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        print(serializer.data)
        serializer.save(submitter=request.user.username)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_customer(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({'success': False, 'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    image_fields = ['legal_person_id_images', 'other_id_images', 'business_license_images', 'bank_account_license_images']
    
    for field in image_fields:
        files = request.FILES.getlist(field)
        saved_paths = []
        for file in files:
            # 生成一个唯一的文件名
            file_name = f"{field}_{file.name}"
            subdirectory = 'customer_images'
            full_path = os.path.join(settings.MEDIA_ROOT, subdirectory, file_name)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # 构建完整的 URL
            relative_url = f"{settings.MEDIA_URL}{subdirectory}/{file_name}"
            full_url = request.build_absolute_uri(relative_url)
            saved_paths.append(full_url)
        
        data[field] = saved_paths
    

    serializer = CustomerSerializer(customer, data=data, partial=True, context={'request': request})
    if serializer.is_valid():
        print(serializer.data)
        serializer.save()
        return Response({'success': True, 'data': serializer.data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
