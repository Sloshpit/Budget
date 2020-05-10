from django.urls import path
from categories.views import CreateCategory, UpdateCategory, DeleteCategory
from . import views

urlpatterns = [
    path('', views.index, name='categories-index'),
    path('add', CreateCategory.as_view(), name='categories-add'),
    path('<int:pk>/update', UpdateCategory.as_view(), name='categories-update'),
    path('<int:pk>/delete', DeleteCategory.as_view(), name='categories-delete'),



]