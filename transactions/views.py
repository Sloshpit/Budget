from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .forms import CreateTransactionForm
from django.shortcuts import render, redirect, reverse

def index(request):
    show_transactions = Transaction.objects.filter(trans_date__range=["2020-04-01", "2020-04-30"])

    template = loader.get_template('transactions/index.html')
    total = Transaction.objects.filter(trans_date__range=["2020-04-01", "2020-04-30"]).aggregate(sum=Sum('amount'))['sum'] or 0.00
    total = "{:.2f}".format(total)
    print (show_transactions)
    context = {
        'show_transactions':show_transactions,
        'total': total,
    }
    return HttpResponse(template.render(context, request))



class TransactionCreate (CreateView):

    template_name = 'transactions/transaction_form.html'
    form_class = CreateTransactionForm
    success_url = reverse_lazy('transaction-index') 
    #model = Transaction
    #fields = '__all__'

class TransactionUpdate (UpdateView):
    template_name = 'transactions/transaction_form.html'
    #form_class = CreateTransactionForm()
    form = CreateTransactionForm
    success_url = reverse_lazy ('transaction-index')
    model = Transaction
    fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']
class TransactionDelete (DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_delete.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('transaction-index')
    fields ='__all__'

class TransactionList (ListView): 
    template_name = 'transactions/index.html'
    form = CreateTransactionForm
    succes_url = reverse_lazy ('transaction-index')
    model = Transaction
    context_object_name = 'show_transactions'
    fields ='__all__'