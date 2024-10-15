from rest_framework import serializers
from .models import Customer
from .permissions import get_user_permissions
from django.utils import timezone
import json

class CustomerSerializer(serializers.ModelSerializer):
    item_permissions = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    update_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('create_time', 'update_time', 'submitter')

    def get_item_permissions(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return get_user_permissions(request.user)
        return {}

    def get_create_time(self, obj):
        return obj.create_time.strftime('%Y-%m-%d %H:%M:%S') if obj.create_time else None

    def get_update_time(self, obj):
        return obj.update_time.strftime('%Y-%m-%d %H:%M:%S') if obj.update_time else None

    def to_internal_value(self, data):

        # 处理日期字段
        date_fields = ['establishment_date', 'license_expiry_date', 'capital_contribution_deadline']
        for field in date_fields:
            if field in data and data[field] == '':
                data[field] = None

        return super().to_internal_value(data)

    def validate(self, data):
        # 验证图片字段
        image_fields = ['legal_person_id_images', 'other_id_images', 'business_license_images', 'bank_account_license_images']
        for field in image_fields:
            if field in data and len(data[field]) > 3:
                raise serializers.ValidationError(f"{field} can have at most 3 images.")
        return data
