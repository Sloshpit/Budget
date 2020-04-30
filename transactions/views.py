from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Transaction
from accounts.models import Account
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .forms import CreateTransactionForm
from django.shortcuts import render, redirect, reverse
from datetime import datetime
from calendar import monthrange


def index(request):
    template = loader.get_template('transactions/index.html')
    today = datetime.today()
    convert_month = datetime.strftime(today, '%b %Y')
    num_days = monthrange(today.year, today.month)
             
    enddate = (today.year, today.month, num_days[1])
    end_year = str(enddate[0])
    end_month = str(enddate[1])
    end_day = str(enddate[2])
    enddate = end_year+"-"+ end_month+ "-" + end_day
             
    first_day = (today.year, today.month, 1)
    start_year = str(first_day[0])
    start_mnth = str(first_day[1])
    start_day = str(first_day[2])
             
    startdate = start_year+"-"+ start_mnth+ "-" + start_day
    show_transactions = Transaction.objects.all()
    total = Transaction.objects.filter(trans_date__range=[startdate, enddate]).aggregate(sum=Sum('amount'))['sum'] or 0.00
    total = "{:.2f}".format(total)

    context = {
        'show_transactions':show_transactions,
        'total': total,
    }
    return HttpResponse(template.render(context, request))

class TransactionCreate (CreateView):

     template_name = 'transactions/transaction_form.html'
     form_class = CreateTransactionForm
     success_url = reverse_lazy('transaction-index') 
     model = Transaction
     def form_valid(self, form):
        trans_date = form.cleaned_data['trans_date']
        amount = form.cleaned_data['amount']
        description = form.cleaned_data ['description']
        acct_name = form.cleaned_data ['account_name']

        self.object = form.save()

        # get the account type
        account_name = Account.objects.filter(account_name=acct_name).latest().values('account_name')
        account_type = Account.objects.filter(account_name=acct_name).latest().values('account_type')
#        acct_balance_date = Account.objects.filter(account_name=acct_name).latest('balance_date')
#        acct_type = Account.objects.filter().latest('balance_date')
#        acct_balance = Account.objects.filter(account_name=acct_name).latest('balance_date')
        print ('---Latest Account Record----------------')
 #       print (acct_balance_date)
  #      print (acct_type)
  #      print (acct_balance)
        print (account_name)
        print (account_type)
        print ('----Close Latest Account Record----------------')
        #if the trasanction date


        return super().form_valid(form)

    #fields = '__all__'

class TransactionUpdate (UpdateView):
    template_name = 'transactions/transaction_form.html'
    form_class = CreateTransactionForm
    success_url = reverse_lazy('transaction-index') 
    #form = CreateTransactionForm
    #success_url = reverse_lazy ('transaction-index')
    model = Transaction
    #fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']


class TransactionDelete (DeleteView):
    model = Transaction
    form_class = CreateTransactionForm
    #success_url = reverse_lazy('transaction-index') 
    template_name = 'transactions/transaction_delete.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('transaction-index')
    #fields ='__all__'

class TransactionList (ListView): 
    template_name = 'transactions/index.html'
    form_class = CreateTransactionForm
    success_url = reverse_lazy ('transaction-index')
    model = Transaction
    context_object_name = 'show_transactions'
    fields ='__all__'