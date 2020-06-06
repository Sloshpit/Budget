from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from .models import Category
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import CategoryForm, UpdateCategoryForm
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
     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user = self.request.user.id)
        return kwargs

     def form_valid(self, form):
        category = form.cleaned_data ['category']
        master_category = form.cleaned_data['master_category']
        user = self.request.user
        form.instance.user = self.request.user   
        form.save()
        return super().form_valid(form)

class UpdateCategory(LoginRequiredMixin, UpdateView):
     template_name = 'categories/categories_form.html'
     form_class = UpdateCategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category
     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user = self.request.user.id)
        return kwargs


class DeleteCategory(LoginRequiredMixin, DeleteView):
     template_name = 'categories/categories_delete.html'
     form_class = CategoryForm
     success_url = reverse_lazy('categories-index') 
     model = Category