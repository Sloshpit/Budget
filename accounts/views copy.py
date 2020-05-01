from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Account, AccountList
from transfers.models import Transfer
from transactions.models import Transaction
from django.shortcuts import render
from .forms import GetDateForm
from datetime import date
import numpy as np

def index(request):
    account_balance_array=[]
    template = loader.get_template('accounts/index.html')
    all_accounts = Account.objects.all()

    print (all_accounts)
    get_accounts = Account.objects.all()
    #print (get_accounts)
    #for account_list in get_account_list:
    #    print (account_list.account_name)
    #    print (account_list.account_type)
    #    print (account_list.initial_balance)
    #    print (account_list.date)
    
    #for account in get_accounts:
    #    print ('-------------------')
    #    print (account.balance_desc)
    #    print (account.account_name)
    #    print (account.balance)
    #    print (account.balance_date)
    #    print ('------------------')


    total_cash = 0
    for account_list in get_account_list:


        #get account name, account type and balance date (today) to load into array
        account_name = account_list.account_name
        account_id = account_list.id

        print ('-----------------')
        print (account_name)
        print ('------------------')
        balance_date = Account.objects.filter(account_name=account).last()
        print (balance_date)

        #get all transactions for current account
        #account_transactions = Transaction.objects.filter(account_name=account.id, trans_date__lte=balance_date).aggregate(sum=Sum('amount'))['sum'] or 0.00
        #get the current account balance (at the moment this is just the initial balance - need to get all transactions from current day forward??)
        #account_balance = Account.objects.filter(account=account_id).last()
        #print (account_balance)
        #get any transfers (likely need to only get stuff from current balance date..otherwise this may mess up if we write a new balance)
       # account_incoming_transfers = Transfer.objects.filter(incoming_account__pk=account.id, transfer_date__lte=balance_date).aggregate(sum=Sum('transfer_amount'))['sum'] or 0.00
       # account_outgoing_transfers = Transfer.objects.filter(outgoing_account__pk=account.id, transfer_date__lte=balance_date).aggregate(sum=Sum('transfer_amount'))['sum'] or 0.00
        #calculate the new balance
        #new_account_balance = account_balance + account_transactions + account_incoming_transfers - account_outgoing_transfers

        #calculate cash position by summing the new balance of each account
        #total_cash = new_account_balance + total_cash
        #build the array for display
        #account_balance_array.append((account_name, account_balance, balance_date))
        print ('yo')    
    #card_total_object = Account.objects.filter(account_type__contains="credit card").values('balance')
    #card_total = card_total_object[0]['balance']
    #other_account_total = Account.objects.exclude(account_type__contains="credit card").aggregate(sum=Sum('balance'))['sum'] or 0.00
    context = {
        'total_cash': total_cash,
        'account_balance_array' : account_balance_array    }
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


