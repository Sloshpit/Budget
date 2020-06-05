from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Account, AccountBalance
from accounthistory.models import AccountHistory
from django.db.models import Max
from transfers.models import Transfer
from transactions.models import Transaction
from categories.models import Category
from django.shortcuts import render
from .forms import GetDateForm, AccountForm
from datetime import date
import numpy as np
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
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
    print ('user')
    print (request.user.id)
    today = date.today()
    account_list = Account.objects.filter(user=request.user).distinct()
    print (account_list)
    latest_account = []

    for account in account_list:
        latest_account.append(AccountBalance.objects.filter(account__account_name=account.account_name, account__user=request.user, balance_date__lte=today).values ('account__account_name', 'balance', 'balance_date','account__id').latest('balance_date'))
        print(latest_account)
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
        account_record = Account.objects.filter(account_name=account_name, user=self.request.user.id)
        print ('account record:')
        print (account_record)
        category = Category.objects.filter(category='Initial Balance', user=self.request.user.id)
        print (category)
        new_record = AccountBalance(account=account_record[0], balance_description = balance_description, balance=initial_balance, balance_date=date.date())        
        new_record.save() 

        initial_balance_transaction = Transaction(user = self.request.user,store=account_name, description = balance_description, amount = initial_balance, trans_date = date.date(), category= category[0], account_name = account_record[0])
        initial_balance_transaction.save()
        new_record_history = AccountHistory(user=self.request.user, account = account_record[0], transaction=initial_balance_transaction, date=date, balance = initial_balance)
        new_record_history.save()
        total_budget_left = 0

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

class ShowTransactions (LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'accounts/details.html'
    context_object_name = 'big_list'
  # def get_queryset(self, **kwargs):
  #      account_id = str(self.kwargs)
  #      print (account_id)
  #      account_name=self.request.GET['account']
  #      print (account_name)
  #      context ['transactions'] =  Transaction.objects.filter(user=self.request.user, account_name__account_name=account_name).order_by('-trans_date')
  #      return (context)
    def get_context_data(self, **kwargs):
        account_name = self.request.GET['account']
        context = super (ShowTransactions, self).get_context_data(**kwargs)
        context ['account_balances']= AccountBalance.objects.filter(account__user=self.request.user, account__account_name = account_name).order_by('-balance_date')
        context ['transactions'] =  Transaction.objects.filter(user=self.request.user, account_name__account_name=account_name).order_by('-trans_date')
        return (context)

def test (request):
        #get all transaction dates for account
        template = loader.get_template ('accounts/test.html')
        account_name = 'Westjet'
        user = '36'
        transaction_dates = Transaction.objects.filter (user=user, account_name__account_name=account_name).values('trans_date').distinct().order_by('-trans_date')
        transactions = Transaction.objects.filter (user=user, account_name__account_name=account_name).order_by('-trans_date')
        latest_transactions = Transaction.objects.filter (user=user, account_name__account_name=account_name).latest('trans_date')
        account_balance = AccountBalance.objects.filter (account__user=user, account__account_name=account_name).values('balance', 'balance_date').order_by('-balance_date')
        print ('account balance -----')
        print (account_balance)
        print (transactions)
        print ('----latest transactions')
        print (latest_transactions)
        context = {
          'transaction_dates': transaction_dates,
          'transactions': transactions,
       }
        return HttpResponse(template.render(context, request))