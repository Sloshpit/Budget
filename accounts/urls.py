from django.urls import path
from accounts.views import CreateAccount, UpdateAccount, DeleteAccount, ShowTransactions
from . import views

urlpatterns = [
    path('', views.index, name='accounts-index'),
    path('add', CreateAccount.as_view(), name='accounts-add'),
    path('<int:pk>/update', UpdateAccount.as_view(), name='accounts-update'),
    path('<int:pk>/delete', DeleteAccount.as_view(), name='accounts-delete'), 
    path('show-transactions', ShowTransactions.as_view(), name='show-transactions'), 
    path ('test', views.test, name='test'),
]