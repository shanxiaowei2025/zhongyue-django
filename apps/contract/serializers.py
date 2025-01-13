from rest_framework import serializers
from .models import Contract

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_no', 'business_type',
            'customer_name', 'customer_code', 'customer_address', 
            'customer_phone', 'customer_contact',
            'company_name', 'company_code', 'company_address',
            'company_phone', 'business_person',
            'amount', 'sign_date', 'start_date', 'expire_date',
            'status', 'remark', 'contract_files',
            'submitter', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
