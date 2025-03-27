from rest_framework import serializers
from .models import FeeStatement 

class FeeStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStatement
        fields = '__all__'  
