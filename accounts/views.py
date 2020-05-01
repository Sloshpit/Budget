from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Account, AccountBalance
from django.db.models import Max
from transfers.models import Transfer
from transactions.models import Transaction
from django.shortcuts import render
from .forms import GetDateForm
from datetime import date
import numpy as np

def index(request):
    template = loader.get_template ('accounts/index.html')
    account_list = Account.objects.values_list('account_name', flat=True).distinct()
    latest_account = []
   # latest_account = []
    for account in account_list:
        latest_account.append(AccountBalance.objects.filter(account__account_name=account).values ('account__account_name', 'balance', 'balance_date').latest('balance_date'))
        #account_name = AccountBalance.objects.filter(account__account_name=account).values('account__account_name').latest('balance_date')
        #balance = AccountBalance.objects.filter(account__account_name=account).values('balance').latest('balance_date')        
        #balance_date = AccountBalance.objects.filter(account__account_name=account).values('balance_date').latest('balance_date')          
        #latest_account.append((account_name, balance_date, balance))
    #current_account_balances = AccountBalance.objects.values('account__account_name').annotate(Max('balance_date'))
    print ('--------------')
    print (latest_account)
    print ('--------------')
    context = {
        'latest_account': latest_account,
       }
    return HttpResponse(template.render(context, request))


def detail(request, account_id):
    template = loader.get_template ('accounts/details.html')
    selected_account = Account.objects.filter(id=account_id).values('account_list')
    acct_name = selected_account[0]['account_list']
    trans_for_account_id = Transaction.objects.filter(account_list=1)
    transaction_total = Transaction.objects.filter(account_list=1).aggregate(sum=Sum('amount'))['sum'] or 0.00
    print (acct_name)
    context ={
        'acct_name': acct_name,
        'trans_for_account_id': trans_for_account_id,
        'transaction_total': transaction_total
    }
    return HttpResponse((template.render(context,request)))


