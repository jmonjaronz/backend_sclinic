from rest_framework import serializers
from .models import Benefit

class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = [
            'id', 'clinic', 'name', 'description', 'benefit_type', 
            'discount_percentage', 'discount_fixed', 'discount_scope',
            'precedence', 'is_exclusive', 'valid_from', 'valid_until',
            'min_age', 'max_age', 'min_previous_visits', 
            'applies_to_all_headquarters', 'is_active'
        ]
        read_only_fields = ['id', 'clinic']

