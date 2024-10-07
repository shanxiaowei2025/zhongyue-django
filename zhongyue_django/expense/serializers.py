from rest_framework import serializers
from .models import Expense
from .permissions import get_user_permissions

class ExpenseSerializer(serializers.ModelSerializer):
    item_permissions = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'

    def get_item_permissions(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return get_user_permissions(request.user)
        return {}
