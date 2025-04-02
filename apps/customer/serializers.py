from rest_framework import serializers
from .models import Customer
import json
from decimal import Decimal

class CustomerSerializer(serializers.ModelSerializer):
    create_time = serializers.SerializerMethodField()
    update_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('create_time', 'update_time', 'submitter')



    def get_create_time(self, obj):
        return obj.create_time.strftime('%Y-%m-%d %H:%M:%S') if obj.create_time else None

    def get_update_time(self, obj):
        return obj.update_time.strftime('%Y-%m-%d %H:%M:%S') if obj.update_time else None

    def to_internal_value(self, data):
        # 处理日期字段
        date_fields = ['establishment_date', 'license_expiry_date', 'capital_contribution_deadline']
        for field in date_fields:
            if field in data and data[field] in ['', None]:
                data[field] = None

        # 处理小数字段
        decimal_fields = ['registered_capital', 'paid_in_capital']
        for field in decimal_fields:
            if field in data:
                if data[field] in [None, '']:
                    data[field] = None
                else:
                    try:
                        data[field] = Decimal(data[field])
                    except InvalidOperation:
                        data[field] = None

        # 处理布尔类型字段 (在模型中存储为CharField)
        boolean_fields = ['has_online_banking', 'is_online_banking_custodian']
        for field in boolean_fields:
            if field in data:
                if data[field] in ['true', 'True', '1', 1, True]:
                    data[field] = 'true'
                elif data[field] in ['false', 'False', '0', 0, False]:
                    data[field] = 'false'
                else:
                    data[field] = None

        return super().to_internal_value(data)

    def validate(self, attrs):
        # 添加额外的验证逻辑（如果需要）
        return attrs
