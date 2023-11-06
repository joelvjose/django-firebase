import re
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny

from .authentication import FirebaseAuthentication
from .models import UserAccount
from .serializers import UserCreateSerializer,UserSerializer

from firebase_admin import auth


class RoutesView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def get(self, request):
        routes = [
            'accounts/register/',
            'accounts/login/',
            'accounts/profile/view/',
            'accounts/profile/edit/',
        ]
        return Response(routes)

class RegisterUser(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def post(self,request):
        username = request.data['username']
        password= request.data['password']
        email = request.data['email']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        try:
            if not email or not password:
                raise ValueError("Email and password are required")
            
            if (email and len(email)>100 ) or (username and len(username)>100 ) or (first_name and len(first_name)>100) or (last_name and len(last_name)>100):
                raise ValueError("Only 100 characters are allowed for a field")
            
            if password and len(password)<8:
                raise ValueError("This password is too short. It must contain at least 8 characters")
            
            if UserAccount.objects.filter(username=username).exists():
                raise ValueError("A user with that username already exists")
            
            
                    
            serializer = UserCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            user = serializer.create(serializer.validated_data)
            serializer = UserCreateSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

class LoginUser(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def post(self,request):
        
        
        user = UserAccount.objects.filter(username=username).first()
        if user is not None:
            hashed_password = user.password
            password_match = check_password(password, hashed_password)
            if password_match:
                print("true")
                uid = user.username
                print(uid)
                token = auth.create_custom_token(uid)
                print(token)
                serializer = UserSerializer(user)
            
                context = {
                    'token': token,
                    'user': serializer.data
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                return Response({'Username or password is invalid'},status=status.HTTP_404_NOT_FOUND) 
        else:
            return Response({'Username or password is invalid'},status=status.HTTP_404_NOT_FOUND) 
        


class ProfileView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ FirebaseAuthentication ]
    
    def get(self,request):
        try:
            username =  request.user.username
            data = UserAccount.objects.get(username = username)
            serializer = UserSerializer(data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status=status.HTTP_404_NOT_FOUND)


class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ FirebaseAuthentication ]
    
    def post(self,request):
        user = request.user
        try:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                if 'username' in request.data:
                    new_username = request.data['username']
                    if UserAccount.objects.exclude(id=user.id).filter(username=new_username).exists():
                        raise ValidationError(f"User already exist with the username '{new_username}'.")
                serializer.save()
                serialized_data = serializer.data
                return Response(serialized_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status=status.HTTP_404_NOT_FOUND)