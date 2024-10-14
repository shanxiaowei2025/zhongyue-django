from rest_framework import serializers
from .models import Customer
from .permissions import get_user_permissions
from django.utils import timezone

class CustomerSerializer(serializers.ModelSerializer):
    item_permissions = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    update_time = serializers.SerializerMethodField()
    legal_person_id_images = serializers.ListField(
        child=serializers.URLField(), required=False
    )
    other_id_images = serializers.ListField(
        child=serializers.URLField(), required=False
    )
    business_license_images = serializers.ListField(
        child=serializers.URLField(), required=False
    )
    bank_account_license_images = serializers.ListField(
        child=serializers.URLField(), required=False
    )

    class Meta:
        model = Customer
        fields = '__all__'

    def get_item_permissions(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return get_user_permissions(request.user)
        return {}

    def get_create_time(self, obj):
        if obj.create_time:
            return timezone.localtime(obj.create_time).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def get_update_time(self, obj):
        if obj.update_time:
            return timezone.localtime(obj.update_time).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def validate_legal_person_id_images(self, value):
        return self._validate_image_list(value)

    def validate_other_id_images(self, value):
        return self._validate_image_list(value)

    def validate_business_license_images(self, value):
        return self._validate_image_list(value)

    def validate_bank_account_license_images(self, value):
        return self._validate_image_list(value)

    def _validate_image_list(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("This field should be a list of URLs.")
        for url in value:
            if not isinstance(url, str):
                raise serializers.ValidationError("Each item in the list should be a URL.")
        return value
