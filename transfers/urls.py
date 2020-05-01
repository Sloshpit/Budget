from django.urls import path
from transfers.views import CreateTransfer
from . import views

urlpatterns = [
    path('', views.index, name='transfers-index'),
    path('add', CreateTransfer.as_view(), name='transfer-add'),

]