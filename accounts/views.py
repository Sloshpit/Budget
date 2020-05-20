from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Account, AccountBalance
from django.db.models import Max
from transfers.models import Transfer
from transactions.models import Transaction
from categories.models import Category
from django.shortcuts import render
from .forms import GetDateForm, AccountForm
from datetime import date
import numpy as np
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from pytz import timezone
import pytz
from tzlocal import get_localzone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required

def index(request):
    print ('in index')
    total_cash = 0
    template = loader.get_template ('accounts/index.html')
    account_list = AccountBalance.objects.filter(account__user=request.user).values_list('account__account_name', flat=True).distinct()
    latest_account = []
    today = str(date.today())
    print (today)
    for account in account_list:
        latest_account.append(AccountBalance.objects.filter(account__account_name=account, balance_date__lte=today, account__user=request.user).values ('account__account_name', 'balance', 'balance_date').latest('balance_date'))
    print (latest_account)

    for account in latest_account:
        total_cash= account['balance'] + total_cash
    
    print (total_cash)
    context = {
          'latest_account': latest_account,
          'total_cash': total_cash,
       }
    return HttpResponse(template.render(context, request))


class CreateAccount(LoginRequiredMixin,CreateView):
     template_name = 'accounts/accounts_form.html'
     form_class = AccountForm
     success_url = reverse_lazy('accounts-index') 
     model = Account

     def form_valid(self, form):
        account_name = form.cleaned_data['account_name']
        initial_balance = form.cleaned_data['initial_balance']
        date = form.cleaned_data ['date']
        account_type = form.cleaned_data['account_type']
        balance_description = 'initial'
        form.instance.user = self.request.user
        self.object = form.save()
        account_record = Account.objects.filter(account_name=account_name)
        category = Category.objects.filter(category='Initial Balance')
        print (category)
        new_record = AccountBalance(account=account_record[0], balance_description = balance_description, balance=initial_balance, balance_date=date.date())        
        new_record.save() 
        initial_balance_transaction = Transaction(store=account_name, description = balance_description, amount = initial_balance, trans_date = date.date(), category= category[0], account_name = account_record[0])
        initial_balance_transaction.save()
        print (initial_balance_transaction)
        return super().form_valid(form)

class UpdateAccount(LoginRequiredMixin,UpdateView):
     template_name = 'accounts/accounts_form.html'
     form_class = AccountForm
     success_url = reverse_lazy('accounts-index') 
     model = Account

class DeleteAccount(LoginRequiredMixin,DeleteView):
     template_name = 'accounts/accounts_delete.html'
     form_class = AccountForm
     success_url = reverse_lazy('accounts-index') 
     model = Account