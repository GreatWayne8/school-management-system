from rest_framework import serializers
from .models import FeeStatement, FeeStructure

class FeeStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStatement
        fields = '__all__'

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'
