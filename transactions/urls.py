from django.urls import path
from transactions.views import TransactionCreate, TransactionDelete, TransactionUpdate, TransactionList

from . import views


urlpatterns = [
 #   path('', views.index, name='transaction-index'),
    path('', TransactionList.as_view(), name='transaction-index'),
#    path('add', views.transactioncreate , name='transactioncreate'),
    path('add', TransactionCreate.as_view(), name='transaction-add'),
    path('<int:pk>/update', TransactionUpdate.as_view(), name='transaction-update'),
    path('<int:pk>/delete', TransactionDelete.as_view(), name='transaction-delete'),

]
