from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from .models import Category
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import CategoryForm
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
@login_required
def index(request):
    template = loader.get_template('categories/index.html')
    show_categories = Category.objects.filter(user=request.user)
    show_transactions = Transaction.objects.all()
    total = Transaction.objects.filter(user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
    total = "{:.2f}".format(total)

    context = {
        'show_categories': show_categories,
        'show_transactions':show_transactions,
        'total': total,
    }
    return HttpResponse(template.render(context, request))

class CreateCategory(LoginRequiredMixin, CreateView):
     template_name = 'categories/categories_form.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category

class UpdateCategory(LoginRequiredMixin, UpdateView):
     template_name = 'categories/categories_form.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category

class DeleteCategory(LoginRequiredMixin, DeleteView):
     template_name = 'categories/categories_delete.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category