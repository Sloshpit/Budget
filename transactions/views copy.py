from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
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
    print ('transactioncreate')
    template_name = 'transactions/transaction_form.html'
    #model = Transaction
    #fields = '__all__'
    form = CreateTransactionForm()
    success_url = reverse_lazy('transaction-index')            
    def add_transaction (self, request):
        form = CreateTransactionForm(request.POST)
        print ('inside add_transaction def')
        if form.is_valid():
            form.save()
            store = form.cleaned_data['store']
            description = form.cleaned_data['description']
            amount = form.cleaned_data['amount']
            trans_date = form.cleaned_data['trans_date']
            category = form.cleaned_data['category']
            account_name = form.cleaned_data ['account_name']
            #return redirect('/transactions/')
        #return reverse('transactions-detail', kwargs={'pk': self.pk})
        #args = {'form':form, 'store':store, 'description':description, 'amount': amount, 'trans_date':trans_date, 'category':category, 'account_name':account_name}
        return render (request, self.template_name)    

class TransactionUpdate (UpdateView):
    model = Transaction
    #fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']
class TransactionDelete (DeleteView):
    model = Transaction
    success_url = reverse_lazy('transaction-list')