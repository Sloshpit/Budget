from django.shortcuts import render
from .models import AccountHistory
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import AccountDropdown
from .filter import AccountFilter
from django_filters.views import FilterView
# Create your views here.


class AcctHistory (LoginRequiredMixin, ListView): 
    template_name = 'accounthistory/index.html'
    model = AccountHistory
    context_object_name = 'show_history'
    fields ='__all__'
    def get_queryset(self):
        qs = (self.model.objects.filter(user=self.request.user).order_by('account', '-date'))
    # print(str(qs.query))   # SQL check is perfect for debugging
        return qs


class AcctHistoryFilter (LoginRequiredMixin, FilterView):
    template_name = 'accounthistory/accountfilter.html'
    model = AccountHistory
    context_object_name = 'show_history'
    filterset_class = AccountFilter
   
    def get_filterset(self, *args, **kwargs):
        fs = super().get_filterset(*args, **kwargs)
        print (fs)
        fs.filters['account'].field.queryset = fs.filters['account'].field.queryset.filter(user=self.request.user)
        fs.filters['account'].field.queryset = fs.filters['account'].field.queryset.all() 
        return fs

    
    def get_queryset(self):
         return AccountHistory.objects.filter(user=self.request.user).order_by('-account','-date')   
