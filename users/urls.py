from django.urls import path
from .views import RoutesView,RegisterUser,LoginUser,ProfileView,EditProfileView

urlpatterns = [
    path('',RoutesView.as_view(),name='getRoutes'),
    path('accounts/register/',RegisterUser.as_view(),name='register'),
    path('accounts/login/',LoginUser.as_view(),name='login'),
    path('accounts/profile/view/', ProfileView.as_view(),name='profile_view'),
    path('accounts/profile/edit/',EditProfileView.as_view(),name='edit_profile')
]