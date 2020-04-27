from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='accounts-index'),
    path('<int:account_id>/', views.detail, name='detail'),
    path('trans-by-date/', views.transactions_by_date, name='transacations_by_date'),
    
] 