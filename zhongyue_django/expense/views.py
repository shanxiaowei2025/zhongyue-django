from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from .models import Expense
from .serializers import ExpenseSerializer
import json
from datetime import datetime, date
from calendar import monthrange
from django.conf import settings
import os
from urllib.parse import urljoin
from django.core.files.storage import default_storage

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_expense_list(request):
    data = json.loads(request.body)
    company_name = data.get('companyName', '')
    status = data.get('status')
    page = data.get('currentPage', 1)
    page_size = data.get('pageSize', 10)

    expenses = Expense.objects.all().order_by('-create_time')
    if company_name:
        expenses = expenses.filter(company_name__icontains=company_name)
    if status is not None:
        expenses = expenses.filter(status=status)

    paginator = Paginator(expenses, page_size)
    expenses_page = paginator.get_page(page)

    serializer = ExpenseSerializer(expenses_page, many=True)
    return Response({
        'success': True,
        'data': {
            'list': serializer.data,
            'total': paginator.count,
            'pageSize': page_size,
            'currentPage': int(page)
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_expense(request):
    data = request.data.copy()
    converted_data = {}
    
    # 处理 contract_image
    if 'contractImage' in data and isinstance(data['contractImage'], dict):
        data['contract_image'] = data['contractImage'].get('url', '')
    
    # 字段名称映射
    field_mapping = {
        'accountingSoftwareFee': 'accounting_software_fee',
        'addressFee': 'address_fee',
        'agencyEndDate': 'agency_end_date',
        'agencyFee': 'agency_fee',
        'agencyStartDate': 'agency_start_date',
        'agencyType': 'agency_type',
        'businessType': 'business_type',
        'chargeDate': 'charge_date',
        'chargeMethod': 'charge_method',
        'companyLocation': 'company_location',
        'companyName': 'company_name',
        'companyType': 'company_type',
        'contractImage': 'contract_image',
        'contractType': 'contract_type',
        'proofOfCharge': 'proof_of_charge',
        'invoiceSoftwareProvider': 'invoice_software_provider',
        'invoiceSoftwareFee': 'invoice_software_fee',
        'invoiceSoftwareStartDate': 'invoice_software_start_date',
        'invoiceSoftwareEndDate': 'invoice_software_end_date',
        'socialInsuranceAgencyFee': 'social_insurance_agency_fee',
        'insuredCount': 'insured_count',
        'insuranceTypes': 'insurance_types',
        'socialInsuranceStartDate': 'social_insurance_start_date',
        'socialInsuranceEndDate': 'social_insurance_end_date',
        'statisticalReportFee': 'statistical_report_fee',
        'statisticalStartDate': 'statistical_start_date',
        'statisticalEndDate': 'statistical_end_date',
        'licenseType': 'license_type',
        'licenseFee': 'license_fee',
        'oneTimeAddressFee': 'one_time_address_fee',
        'brandFee': 'brand_fee',
        'sealFee': 'seal_fee',
        'changeFee': 'change_fee',
        'changeBusiness': 'change_business',
        'administrativeLicense': 'administrative_license',
        'administrativeLicenseFee': 'administrative_license_fee',
        'otherBusiness': 'other_business',
        'otherBusinessFee': 'other_business_fee',
        'totalFee': 'total_fee',
        'submitter': 'submitter',
        'status': 'status',
        'auditor': 'auditor',
        'auditDate': 'audit_date',
        'createTime': 'create_time',
        'remarks': 'remarks'
    }

    # 创建反向映射
    reverse_field_mapping = {v: k for k, v in field_mapping.items()}

    # 转换字段名称
    for key, value in data.items():
        converted_key = field_mapping.get(key, key)
        converted_data[converted_key] = value

    # 处理文件字段
    file_fields = {
        'contract_image': 'contract_images',
        'proof_of_charge': 'proof_of_charge'
    }
    for file_field, subdirectory in file_fields.items():
        frontend_field = reverse_field_mapping.get(file_field)
        if frontend_field in request.FILES:
            file = request.FILES[frontend_field]
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
            file_path = os.path.join('media', subdirectory, filename)
            full_path = os.path.join(settings.MEDIA_ROOT, subdirectory, filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # 构建完整的 URL
            relative_url = f"{settings.MEDIA_URL}{subdirectory}/{filename}"
            full_url = request.build_absolute_uri(relative_url)
            converted_data[file_field] = full_url

    # 处理金额字段，将空字符串转换为 None
    fee_fields = [
        'license_fee', 'one_time_address_fee', 'brand_fee', 'seal_fee',
        'agency_fee', 'accounting_software_fee', 'address_fee',
        'invoice_software_fee', 'social_insurance_agency_fee',
        'statistical_report_fee', 'change_fee',
        'administrative_license_fee', 'other_business_fee'
    ]
    for field in fee_fields:
        if field in converted_data and converted_data[field] == '':
            converted_data[field] = None

    # 处理日期字段
    start_date_fields = ['agency_start_date', 'invoice_software_start_date', 'social_insurance_start_date', 'statistical_start_date']
    end_date_fields = ['agency_end_date', 'invoice_software_end_date', 'social_insurance_end_date', 'statistical_end_date']

    def process_date(date_str, is_end_date=False):
        if not date_str:
            return None
        try:
            # 尝试解析完整的日期格式 (YYYY-MM-DD)
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # 如果失败，尝试解析年月格式 (YYYY-MM)
                year, month = map(int, date_str.split('-'))
                if is_end_date:
                    _, last_day = monthrange(year, month)
                    parsed_date = date(year, month, last_day)
                else:
                    parsed_date = date(year, month, 1)
            except ValueError:
                # 如果两种格式都解析失败，返回 None
                return None
        
        return parsed_date

    for field in start_date_fields + end_date_fields:
        if field in converted_data:
            is_end_date = field in end_date_fields
            processed_date = process_date(converted_data[field], is_end_date)
            converted_data[field] = processed_date

    # 特殊处理 charge_date，因为它总是需要完整的日期
    if 'charge_date' in converted_data and converted_data['charge_date']:
        processed_date = process_date(converted_data['charge_date'])
        if processed_date:
            converted_data['charge_date'] = processed_date
        else:
            converted_data['charge_date'] = None

    # 处理收费凭证
    proof_of_charge_urls = []
    for i in range(3):  # 最多处理3个文件
        file_key = f'proofOfCharge_{i}'
        if file_key in request.FILES:
            file = request.FILES[file_key]
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
            file_path = os.path.join('proof_of_charge', filename)
            full_path = default_storage.save(file_path, file)
            file_url = request.build_absolute_uri(settings.MEDIA_URL + full_path)
            proof_of_charge_urls.append(file_url)
        elif file_key in data and data[file_key]:
            # 如果是已存在的URL，直接添加
            proof_of_charge_urls.append(data[file_key])

    converted_data['proof_of_charge'] = proof_of_charge_urls

    serializer = ExpenseSerializer(data=converted_data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_expense(request):
    expense_id = request.data.get('id')
    try:
        expense = Expense.objects.get(id=expense_id)
        data = request.data.copy()
        converted_data = {}
        
        # 字段名称映射
        field_mapping = {
            'accountingSoftwareFee': 'accounting_software_fee',
            'addressFee': 'address_fee',
            'agencyEndDate': 'agency_end_date',
            'agencyFee': 'agency_fee',
            'agencyStartDate': 'agency_start_date',
            'agencyType': 'agency_type',
            'businessType': 'business_type',
            'chargeDate': 'charge_date',
            'chargeMethod': 'charge_method',
            'companyLocation': 'company_location',
            'companyName': 'company_name',
            'companyType': 'company_type',
            'contractImage': 'contract_image',
            'contractType': 'contract_type',
            'proofOfCharge': 'proof_of_charge',
            'invoiceSoftwareProvider': 'invoice_software_provider',
            'invoiceSoftwareFee': 'invoice_software_fee',
            'invoiceSoftwareStartDate': 'invoice_software_start_date',
            'invoiceSoftwareEndDate': 'invoice_software_end_date',
            'socialInsuranceAgencyFee': 'social_insurance_agency_fee',
            'insuredCount': 'insured_count',
            'insuranceTypes': 'insurance_types',
            'socialInsuranceStartDate': 'social_insurance_start_date',
            'socialInsuranceEndDate': 'social_insurance_end_date',
            'statisticalReportFee': 'statistical_report_fee',
            'statisticalStartDate': 'statistical_start_date',
            'statisticalEndDate': 'statistical_end_date',
            'licenseType': 'license_type',
            'licenseFee': 'license_fee',
            'oneTimeAddressFee': 'one_time_address_fee',
            'brandFee': 'brand_fee',
            'sealFee': 'seal_fee',
            'changeFee': 'change_fee',
            'changeBusiness': 'change_business',
            'administrativeLicense': 'administrative_license',
            'administrativeLicenseFee': 'administrative_license_fee',
            'otherBusiness': 'other_business',
            'otherBusinessFee': 'other_business_fee',
            'totalFee': 'total_fee',
            'submitter': 'submitter',
            'status': 'status',
            'auditor': 'auditor',
            'auditDate': 'audit_date',
            'createTime': 'create_time',
            'remarks': 'remarks'
        }

        # 创建反向映射
        reverse_field_mapping = {v: k for k, v in field_mapping.items()}

        # 转换字段名称
        for key, value in data.items():
            converted_key = field_mapping.get(key, key)
            converted_data[converted_key] = value

        # 处理文件字段
        file_fields = {
            'contract_image': 'contract_images',
            'proof_of_charge': 'proof_of_charge'
        }
        for file_field, subdirectory in file_fields.items():
            frontend_field = reverse_field_mapping.get(file_field)
            if frontend_field in request.FILES:
                # 如果有新文件上传，处理新文件
                file = request.FILES[frontend_field]
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
                file_path = os.path.join('media', subdirectory, filename)
                full_path = os.path.join(settings.MEDIA_ROOT, subdirectory, filename)
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                relative_url = f"{settings.MEDIA_URL}{subdirectory}/{filename}"
                full_url = request.build_absolute_uri(relative_url)
                converted_data[file_field] = full_url
            elif frontend_field in data:
                # 如果前端传来的是 URL 或 null，直接使用该值
                converted_data[file_field] = data[frontend_field]
            else:
                # 如果前端没有传递该字段，保留原来的值
                converted_data[file_field] = getattr(expense, file_field)

        # 处理金额字段，将空字符串转换为 None
        fee_fields = [
            'license_fee', 'one_time_address_fee', 'brand_fee', 'seal_fee',
            'agency_fee', 'accounting_software_fee', 'address_fee',
            'invoice_software_fee', 'social_insurance_agency_fee',
            'statistical_report_fee', 'change_fee',
            'administrative_license_fee', 'other_business_fee'
        ]
        for field in fee_fields:
            if field in converted_data and converted_data[field] == '':
                converted_data[field] = None

        # 处理日期字段
        start_date_fields = ['agency_start_date', 'invoice_software_start_date', 'social_insurance_start_date', 'statistical_start_date']
        end_date_fields = ['agency_end_date', 'invoice_software_end_date', 'social_insurance_end_date', 'statistical_end_date']

        def process_date(date_str, is_end_date=False):
            if not date_str:
                return None
            try:
                # 尝试解析完整的日期格式 (YYYY-MM-DD)
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                try:
                    # 如果失败，尝试解析年月格式 (YYYY-MM)
                    year, month = map(int, date_str.split('-'))
                    if is_end_date:
                        _, last_day = monthrange(year, month)
                        parsed_date = date(year, month, last_day)
                    else:
                        parsed_date = date(year, month, 1)
                except ValueError:
                    # 如果两种格式都解析失败，返回 None
                    return None
            
            return parsed_date

        for field in start_date_fields + end_date_fields:
            if field in converted_data:
                is_end_date = field in end_date_fields
                processed_date = process_date(converted_data[field], is_end_date)
                converted_data[field] = processed_date

        # 特殊处理 charge_date，因为它总是需要完整的日期
        if 'charge_date' in converted_data and converted_data['charge_date']:
            processed_date = process_date(converted_data['charge_date'])
            if processed_date:
                converted_data['charge_date'] = processed_date
            else:
                converted_data['charge_date'] = None

        # 处理收费凭证
        proof_of_charge_urls = []
        for i in range(3):  # 最多处理3个文件
            file_key = f'proofOfCharge_{i}'
            if file_key in request.FILES:
                file = request.FILES[file_key]
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
                file_path = os.path.join('proof_of_charge', filename)
                full_path = default_storage.save(file_path, file)
                file_url = request.build_absolute_uri(settings.MEDIA_URL + full_path)
                proof_of_charge_urls.append(file_url)
            elif file_key in data and data[file_key]:
                # 如果是已存在的URL，直接添加
                proof_of_charge_urls.append(data[file_key])

        if proof_of_charge_urls:
            converted_data['proof_of_charge'] = proof_of_charge_urls
        
        serializer = ExpenseSerializer(expense, data=converted_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Expense.DoesNotExist:
        return Response({'success': False, 'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_expense(request):
    expense_id = request.data.get('id')
    try:
        expense = Expense.objects.get(id=expense_id)
        expense.delete()
        return Response({'success': True, 'message': 'Expense deleted successfully'}, status=status.HTTP_200_OK)
    except Expense.DoesNotExist:
        return Response({'success': False, 'message': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)