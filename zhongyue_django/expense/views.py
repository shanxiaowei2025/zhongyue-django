from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from .models import Expense
from .serializers import ExpenseSerializer
import json
from django.core.files.base import ContentFile
import base64

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

    # 处理合同图片
    contract_image = request.FILES.get('contractImage')
    if contract_image:
        data['contract_image'] = contract_image

    # 处理收费凭证
    proof_of_charge = request.FILES.get('proofOfCharge')
    if proof_of_charge:
        data['proof_of_charge'] = proof_of_charge

    # 处理日期字段
    date_fields = ['agency_start_date', 'agency_end_date', 'invoice_software_start_date', 
                   'invoice_software_end_date', 'social_insurance_start_date', 'social_insurance_end_date', 
                   'statistical_start_date', 'statistical_end_date', 'charge_date']
    for field in date_fields:
        if field in data and data[field]:
            if '-' not in data[field]:
                data[field] += '-01'  # 添加日期，如果只有年月

    serializer = ExpenseSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_expense(request):
    expense_id = request.data.get('id')
    try:
        expense = Expense.objects.get(id=expense_id)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
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