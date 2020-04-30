from django.urls import path
from django.conf.urls import url
from budgettracker.views import BudgettrackerCreate, BudgettrackerDelete, BudgettrackerUpdate
from . import views


urlpatterns = [
    path('', views.index, name='budgettracker-index'),
    path('add', BudgettrackerCreate.as_view(), name='budgettracker-add'),
    path('<int:pk>/update', BudgettrackerUpdate.as_view(), name='budgettracker-update'),
    path('<int:pk>/delete', BudgettrackerUpdate.as_view(), name='budgettracker-delete'),
    path('get_cat_budget/', views.get_cat_budget, name='get_cat_budget'),
]
