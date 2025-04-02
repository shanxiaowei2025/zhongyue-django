from rest_framework import serializers
from .models import Expense
from django.utils import timezone

class ExpenseSerializer(serializers.ModelSerializer):
    create_time = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'


    def get_create_time(self, obj):
        if obj.create_time:
            return timezone.localtime(obj.create_time).strftime('%Y-%m-%d %H:%M:%S')
        return None
