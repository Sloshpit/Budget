from django.urls import path
from accounthistory.views import AcctHistory, AcctHistoryFilter
from . import views

urlpatterns = [
    path('', AcctHistory.as_view(), name='account-history'),
    path ('accountfilter',AcctHistoryFilter.as_view(), name='acct-history-filter'),
]