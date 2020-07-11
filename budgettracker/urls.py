from django.urls import path
from budgettracker.views import BudgettrackerCreate, BudgettrackerUpdate, BudgettrackerDelete
from . import views

urlpatterns = [
    path('', views.index, name='budgettracker-index'),
    path('add', BudgettrackerCreate.as_view(), name='budgetracker-add'),
    path('<int:pk>/update', BudgettrackerUpdate.as_view(), name='budgettracker-update'),
    path('<int:pk>/delete', BudgettrackerDelete.as_view(), name='budgettracker-delete'),
    path ('test',views.test, name='test'),
    path ('ajax/get_budget_average', views.get_budget_average, name='get-budget-average'),
    path ('ajax/check_max_date', views.check_max_date, name='check_max_date'),
    path ('budget-list', views.budget_list, name='budget-list'),

]