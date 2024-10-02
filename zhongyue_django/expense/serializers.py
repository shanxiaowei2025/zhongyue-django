from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'total_fee')

    def to_internal_value(self, data):
        # 移除设置默认值的逻辑
        return super().to_internal_value(data)

    def create(self, validated_data):
        # 计算总费用，忽略 None 值
        total_fee = sum([
            validated_data.get(fee_field) or 0
            for fee_field in [
                'license_fee', 'one_time_address_fee', 'brand_fee', 'seal_fee',
                'agency_fee', 'accounting_software_fee', 'address_fee',
                'invoice_software_fee', 'social_insurance_agency_fee',
                'statistical_report_fee', 'change_fee',
                'administrative_license_fee', 'other_business_fee'
            ]
        ])
        validated_data['total_fee'] = total_fee if total_fee > 0 else None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 计算总费用，忽略 None 值
        total_fee = sum([
            validated_data.get(fee_field, getattr(instance, fee_field)) or 0
            for fee_field in [
                'license_fee', 'one_time_address_fee', 'brand_fee', 'seal_fee',
                'agency_fee', 'accounting_software_fee', 'address_fee',
                'invoice_software_fee', 'social_insurance_agency_fee',
                'statistical_report_fee', 'change_fee',
                'administrative_license_fee', 'other_business_fee'
            ]
        ])
        validated_data['total_fee'] = total_fee if total_fee > 0 else None

        return super().update(instance, validated_data)
