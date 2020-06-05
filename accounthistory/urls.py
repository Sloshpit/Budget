from django.urls import path
from accounthistory.views import AcctHistory
from . import views

urlpatterns = [
    path('', AcctHistory.as_view(), name='account-history'),
]