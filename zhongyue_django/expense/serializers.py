from rest_framework import serializers
from .models import Expense
import json

class ExpenseSerializer(serializers.ModelSerializer):
    proof_of_charge = serializers.ListField(
        child=serializers.URLField(),
        max_length=3,
        required=False
    )

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

    def validate_proof_of_charge(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("最多只能上传3张收费凭证。")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if isinstance(representation['proof_of_charge'], str):
            try:
                representation['proof_of_charge'] = json.loads(representation['proof_of_charge'])
            except json.JSONDecodeError:
                representation['proof_of_charge'] = []
        return representation

    def validate_contract_image(self, value):
        if isinstance(value, dict):
            return value.get('url', '')
        return value
