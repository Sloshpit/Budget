from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from accounts.models import Account, AccountBalance
from .models import Transfer
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import TransferForm
from django.urls import reverse_lazy
from datetime import datetime


def index(request):
    template = loader.get_template('transfers/index.html')
    show_transfers = Transfer.objects.all()

    context = {
        'show_transfers': show_transfers,
    }
    return HttpResponse(template.render(context, request))

#Default Creatview that takes in incoming & outgoing accounts, amount, transfer date
#Need to calculate a new AccountBalance for both the incoming and outgoing accounts

class CreateTransfer(CreateView):
    template_name = 'transfers/transfer_form.html'
    success_url = reverse_lazy('transfers-index')  
    form_class = TransferForm

    def form_valid(self, form):
        transfer_date = form.cleaned_data['transfer_date']
        transfer_amount = form.cleaned_data['transfer_amount']
        incoming_account = form.cleaned_data ['incoming_account']
        outgoing_account = form.cleaned_data ['outgoing_account']
        self.object = form.save()

        balance_description = "Account Transfer from "+str(incoming_account) +" "+ "To " +str(outgoing_account)
        #last_account_for_account_name = AccountBalance.objects.filter(account_name=acct_name).last()
        latest_incoming_account = AccountBalance.objects.filter(account__account_name=incoming_account).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
        latest_outgoing_account = AccountBalance.objects.filter(account__account_name=outgoing_account).values('account__account_name', 'balance', 'balance_date').latest('balance_date')

        incoming_account_balance=latest_incoming_account['balance']
        outgoing_account_balance=latest_outgoing_account['balance']
        new_incoming_balance=transfer_amount + float(incoming_account_balance)
        new_outgoing_balance=float(outgoing_account_balance) - transfer_amount
        print('-----incoming balance')
        print (new_incoming_balance)
        print ('-----outgoing balance')
        print (new_outgoing_balance)
  
        now = datetime.today()
        print (now)
        new_incoming_record = AccountBalance(account=incoming_account, balance_description = balance_description, balance=new_incoming_balance, balance_date=now)
        new_outgoing_record = AccountBalance(account=outgoing_account, balance_description = balance_description, balance=new_outgoing_balance, balance_date=now)

        new_incoming_record.save()
        new_outgoing_record.save()
       
        return super().form_valid(form)
  