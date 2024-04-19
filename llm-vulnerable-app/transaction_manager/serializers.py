from django.utils import timezone
from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'date', 'created_at','amount', 'description', 'updated_at']
        read_only_fields = ['user', 'date', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        else:
            raise serializers.ValidationError("User is required")

        date = timezone.now()

        validated_data['user'] = user
        validated_data['date'] = date
        return super().create(validated_data)
