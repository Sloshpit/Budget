from django.urls import path
from transactions.views import TransactionCreate, TransactionDelete, TransactionUpdate

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('add', TransactionCreate.as_view(), name='transaction-add'),
    path('<int:pk>/', TransactionUpdate.as_view(), name='transaction-update'),
    path('<int:pk>/delete', TransactionDelete.as_view(), name='transaction-delete'),
]
