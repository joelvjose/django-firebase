from django.db import models
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.
class UserAccountManager(BaseUserManager):
    def create_user(self,email,password,username=None,first_name=None,last_name=None,):
        
        if username == "":
                username = email.split('@')[0]
                username = re.sub(r'\W+', '', username).lower()
                base_username = username
                suffix = 1
                while UserAccount.objects.filter(username=username).exists():
                    username = f'{base_username}{suffix}'
                    suffix += 1
                    
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,username,email,password):
        user = self.create_user(
            email=self.normalize_email(email),
            username= username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class UserAccount(AbstractBaseUser):
    username    = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email       = models.EmailField(max_length=100, unique=True)
    first_name  = models.CharField(max_length=100,null=True,blank=True)
    last_name   = models.CharField(max_length=100,null=True,blank=True)
    
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_superuser   = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserAccountManager()
    
    def __str__(self):
        return self.email