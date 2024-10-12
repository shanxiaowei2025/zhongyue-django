from rest_framework import serializers
from .models import Expense
from .permissions import get_user_permissions
from django.utils import timezone

class ExpenseSerializer(serializers.ModelSerializer):
    item_permissions = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()

    class Meta:
        model = Expense
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
