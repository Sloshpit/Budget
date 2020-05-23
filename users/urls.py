from django.urls import path
from . import views
from users.views import RegisterView, LoginView, PasswordResetView, PasswordChangeView, PasswordChangeDoneView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.contrib.auth import views as auth_views
urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path ('login/',LoginView.as_view(), name='login'),
    path ('logout/',auth_views.LogoutView.as_view(), name='logout'),
    path ('password-reset/',PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
 

]