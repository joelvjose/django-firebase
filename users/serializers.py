from rest_framework import serializers
from .models import UserAccount

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        # fields = '__all__'
        fields = ['username','email','password']
        extra_kwargs={
            'email':{'required': True},
            'password':{'write_only':True}
        }
        
    def create(self,validated_data):
        return UserAccount.objects.create_user(**validated_data)
    
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAccount
        fields = ['email', 'username', 'full_name']
        
    def get_full_name(self, obj):
        return f'{obj.first_name}-{obj.last_name}'
    