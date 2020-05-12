from django.urls import path
from budgettracker.views import BudgettrackerCreate, BudgettrackerUpdate, BudgettrackerDelete
from . import views

urlpatterns = [
    path('', views.index, name='budgettracker-index'),
    path('add', BudgettrackerCreate.as_view(), name='budgetracker-add'),
    path('<int:pk>/update', BudgettrackerUpdate.as_view(), name='budgettracker-update'),
    path('<int:pk>/delete', BudgettrackerDelete.as_view(), name='budgettracker-delete'),

 

]