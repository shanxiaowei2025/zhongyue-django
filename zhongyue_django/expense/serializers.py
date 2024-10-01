from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'total_fee')

    def create(self, validated_data):
        # 计算总费用
        total_fee = sum([
            validated_data.get('license_fee', 0),
            validated_data.get('one_time_address_fee', 0),
            validated_data.get('brand_fee', 0),
            validated_data.get('seal_fee', 0),
            validated_data.get('agency_fee', 0),
            validated_data.get('accounting_software_fee', 0),
            validated_data.get('address_fee', 0),
            validated_data.get('invoice_software_fee', 0),
            validated_data.get('social_insurance_agency_fee', 0),
            validated_data.get('statistical_report_fee', 0),
            validated_data.get('change_fee', 0),
            validated_data.get('administrative_license_fee', 0),
            validated_data.get('other_business_fee', 0),
        ])
        validated_data['total_fee'] = total_fee

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 计算总费用
        total_fee = sum([
            validated_data.get('license_fee', instance.license_fee),
            validated_data.get('one_time_address_fee', instance.one_time_address_fee),
            validated_data.get('brand_fee', instance.brand_fee),
            validated_data.get('seal_fee', instance.seal_fee),
            validated_data.get('agency_fee', instance.agency_fee),
            validated_data.get('accounting_software_fee', instance.accounting_software_fee),
            validated_data.get('address_fee', instance.address_fee),
            validated_data.get('invoice_software_fee', instance.invoice_software_fee),
            validated_data.get('social_insurance_agency_fee', instance.social_insurance_agency_fee),
            validated_data.get('statistical_report_fee', instance.statistical_report_fee),
            validated_data.get('change_fee', instance.change_fee),
            validated_data.get('administrative_license_fee', instance.administrative_license_fee),
            validated_data.get('other_business_fee', instance.other_business_fee),
        ])
        validated_data['total_fee'] = total_fee

        return super().update(instance, validated_data)
