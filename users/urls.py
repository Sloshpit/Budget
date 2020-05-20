from django.urls import path
from . import views
from users.views import RegisterView, LoginView
from django.contrib.auth import views as auth_views
urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path ('login/',LoginView.as_view(), name='login'),
    path ('logout/',auth_views.LogoutView.as_view(), name='logout')

 

]