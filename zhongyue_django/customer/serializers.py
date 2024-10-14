from rest_framework import serializers
from .models import Customer
from .permissions import get_user_permissions
from django.utils import timezone

class CustomerSerializer(serializers.ModelSerializer):
    item_permissions = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    update_time = serializers.SerializerMethodField()

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

