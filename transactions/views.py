from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Transaction
from accounts.models import Account,AccountBalance
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .forms import CreateTransactionForm, UpdateTransactionForm
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
        store = form.cleaned_data ['store']
        category = form.cleaned_data ['category']
        acct_name = form.cleaned_data['account_name']
        amount = form.cleaned_data['amount']
        trans_date = form.cleaned_data['trans_date']
        print (type(trans_date))
        self.object = form.save()
        now = datetime.today()
        print (type(now))
        balance_description = str(store) +" "+ str(category)

        if now.date() == trans_date.date():
        #if record is equal to today
        #last_account_for_account_name = AccountBalance.objects.filter(account_name=acct_name).last()
            latest_account = AccountBalance.objects.filter(account__account_name=acct_name).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
            account_balance=latest_account['balance']
            new_account_balance=amount + float(account_balance)        
            new_record = AccountBalance(account=acct_name, balance_description = balance_description, balance=new_account_balance, balance_date=trans_date)
            new_record.save()
        else:
           #the transaction is in the past so you need to add a new balance and update all the other balances


           print ('from here calculate a new_record ')
           records_to_update = AccountBalance.objects.filter(balance_date__gte=trans_date, balance_date__lte = now)
           print (records_to_update)

           for record in records_to_update:
                record.balance = record.balance + amount
                record.save()   
           latest_account = AccountBalance.objects.filter(balance_date__lt=trans_date).order_by("-balance_date")[0]
           print ('------in else---got the latest record in the past')
           print (latest_account)
           account_balance=latest_account.balance
           new_account_balance=amount + float(account_balance)        
           new_record = AccountBalance(account=acct_name, balance_description = balance_description, balance=new_account_balance, balance_date=trans_date)
           new_record.save() 
       
        return super().form_valid(form)

    #fields = '__all__'

class TransactionUpdate (UpdateView):
    template_name = 'transactions/transaction_form.html'
    form_class = UpdateTransactionForm
    success_url = reverse_lazy('transaction-index') 
    #form = CreateTransactionForm
    #success_url = reverse_lazy ('transaction-index')
    model = Transaction
    #fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']
    #get the date of the transaction
    #get all the transactions from that date to present date (today)
    #perform calculation on the updated balance for each
    #write the balance to the db, along with any other changes.

    def form_valid(self, form):
        self.object = self.get_object()
        today = datetime.today()
        store = form.cleaned_data ['store']
        category = form.cleaned_data ['category']
        acct_name = form.cleaned_data['account_name']
        amount = form.cleaned_data['amount']
        print ('-------get-object')
        print (self.get_object())
        print (self.object.amount)
        print ('-----------------')
        amount_difference = amount - self.object.amount
        print ('difference:')
        print (amount_difference)
        trans_date = form.cleaned_data['trans_date']
        balance_records = AccountBalance.objects.filter(account__account_name=acct_name, balance_date__range = [trans_date, today]  )
        for record in balance_records:
            record.balance = record.balance + amount_difference
            record.save()
        return super().form_valid(form)

class TransactionDelete (DeleteView):
    model = Transaction
    form_class = CreateTransactionForm
    #success_url = reverse_lazy('transaction-index') 
    template_name = 'transactions/transaction_delete.html'
#    context_object_name = 'transaction'
    success_url = reverse_lazy('transaction-index')
    #fields ='__all__'


    def delete(self, *args, **kwargs):
        today = datetime.today()
        self.object = self.get_object()
        print (self.object)
        amount = self.object.amount
        trans_date = self.object.trans_date
        acct_name = self.object.account_name
        account_record_to_delete = AccountBalance.objects.filter(balance_date=trans_date, account=acct_name).delete()
        records_to_update = AccountBalance.objects.filter(balance_date__gte=trans_date, balance_date__lte = today)

        for record in records_to_update:
            record.balance = record.balance - amount
            record.save()
        
        return super(TransactionDelete, self).delete(*args, **kwargs)

class TransactionList (ListView): 
    template_name = 'transactions/index.html'
    form_class = CreateTransactionForm
    success_url = reverse_lazy ('transaction-index')
    model = Transaction
    context_object_name = 'show_transactions'
    fields ='__all__'