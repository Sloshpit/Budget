from django.shortcuts import render
from .models import AccountHistory
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

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