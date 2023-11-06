
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

# import pyrebase

# config = {
#   "apiKey": "AIzaSyBGlB7SuHsUKEvzkQitzglxyeO43oo2up4",
#   "authDomain": "bewyse-51205.firebaseapp.com",
#   "projectId": "bewyse-51205",
#   "storageBucket": "bewyse-51205.appspot.com",
#   "messagingSenderId": "332397128589",
#   "databaseURL": "https://databaseName.firebaseio.com",
#   "appId": "1:332397128589:web:74ddc438967726325d6bc4",
#   "measurementId": "G-MG915TM1RS"
# }

# firebase = pyrebase.initialize_app(config)
# pyrebase_auth = firebase.auth()


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
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        user = serializer.create(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginUser(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def post(self,request):
        username = request.data['username']
        password= request.data['password']
        
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [ FirebaseAuthentication ]
    
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
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)