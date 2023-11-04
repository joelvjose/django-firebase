from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib import auth
from firebase_admin import auth as firebase_auth
from rest_framework.exceptions import AuthenticationFailed
from .authentication import FirebaseAuthentication
from django.core.exceptions import ValidationError

from BeWyse.users.models import UserAccount

from .serializers import UserCreateSerializer,UserSerializer
from BeWyse.users import authentication

# Create your views here.
@api_view(['GET'])
def getRoutes(request):
    routes = [
        'accounts/register/',
        'accounts/login/',
        'accounts/profile/view/',
        'accounts/profile/edit/',
    ]
    
    return Response(routes)

class RegisterUser(APIView):
    def post(self,request):
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        user = serializer.create(serializer.validated_data)

        return Response(user, status=status.HTTP_201_CREATED)

class LoginUser(APIView):
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def post(self,request):
        username = request.data['username']
        password= request.data['password']
        user = auth.authenticate(request, username = username, password = password)
        try:
            if user is not None:
                user_data=UserAccount.objects.filter(username=user).first()
                auth.login(request, user)
                uid = user_data.username
                token = firebase_auth.create_custom_token(uid)
                serializer = UserSerializer(user)
            
                context = {
                    'token': token,
                    'user': serializer.data
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                raise AuthenticationFailed('Username or password is invalid')
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ProfileView(APIView):
    authentication_classes = [ FirebaseAuthentication ]
    
    def get(self,request):
        try:
            data = UserAccount.objects.get(username = request.user)
            serializer = UserSerializer(data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class EditProfileView(APIView):
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
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)