from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from .models import Category
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import CategoryForm
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy


def index(request):
    template = loader.get_template('categories/index.html')
    show_categories = Category.objects.all()
    show_transactions = Transaction.objects.all()
    total = Transaction.objects.all().aggregate(sum=Sum('amount'))['sum'] or 0.00
    total = "{:.2f}".format(total)

    context = {
        'show_categories': show_categories,
        'show_transactions':show_transactions,
        'total': total,
    }
    return HttpResponse(template.render(context, request))

class CreateCategory(CreateView):
     template_name = 'categories/categories_form.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category

class UpdateCategory(UpdateView):
     template_name = 'categories/categories_form.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category

class DeleteCategory(DeleteView):
     template_name = 'categories/categories_delete.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category