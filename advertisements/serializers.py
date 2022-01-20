from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at',
        )

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        quantity = Advertisement.objects.filter(creator=self.context["request"].user, status='OPEN').count()
        method = self.context['request'].method
        message = 'Too many advertisement are open. Max count 10'
        if method == 'POST' and quantity > 9:
            raise ValidationError(detail=message)
        if (method == 'PATCH' or method == 'PUT') and data.get('status') == 'OPEN' and quantity > 9:
            raise ValidationError(detail=message)
        return data
