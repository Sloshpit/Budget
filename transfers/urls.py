from django.urls import path
from transfers.views import CreateTransfer, UpdateTransfer, DeleteTransfer
from . import views

urlpatterns = [
    path('', views.index, name='transfers-index'),
    path('add', CreateTransfer.as_view(), name='transfer-add'),
    path('<int:pk>/update', UpdateTransfer.as_view(), name='transfer-update'),
    path('<int:pk>/delete', DeleteTransfer.as_view(), name='transfer-delete'),

 

]