from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('id', 'create_time', 'submitter')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['submitter'] = user.id
        return super().create(validated_data)
