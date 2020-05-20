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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required

def index(request):
    template = loader.get_template('transfers/index.html')
    show_transfers = Transfer.objects.filter(user=request.user)

    context = {
        'show_transfers': show_transfers,
    }
    return HttpResponse(template.render(context, request))

#Default Creatview that takes in incoming & outgoing accounts, amount, transfer date
#Need to calculate a new AccountBalance for both the incoming and outgoing accounts

class CreateTransfer(LoginRequiredMixin, CreateView):
    template_name = 'transfers/transfer_form.html'
    success_url = reverse_lazy('transfers-index')  
    form_class = TransferForm

    def form_valid(self, form):

        transfer_date = form.cleaned_data['transfer_date']
        transfer_amount = form.cleaned_data['transfer_amount']
        incoming_account = form.cleaned_data ['incoming_account']
        outgoing_account = form.cleaned_data ['outgoing_account']
        form.instance.user = self.request.user   
 
        self.object = form.save()
        now = datetime.today()
        print (transfer_date)

        balance_description = "Account Transfer from "+str(incoming_account) +" "+ "To " +str(outgoing_account)
        
        if now == transfer_date:
             latest_incoming_account = AccountBalance.objects.filter(account__account_name=incoming_account, account__user=self.request.user).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
             print (latest_incoming_account)
             latest_outgoing_account = AccountBalance.objects.filter(account__account_name=outgoing_account, account__user=self.request.user).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
             incoming_account_balance=latest_incoming_account['balance']
             outgoing_account_balance=latest_outgoing_account['balance']
             new_incoming_balance=transfer_amount + float(incoming_account_balance)
             new_outgoing_balance=float(outgoing_account_balance) - transfer_amount
             new_incoming_record = AccountBalance(account=incoming_account, balance_description = balance_description, balance=new_incoming_balance, balance_date=transfer_date)
             new_outgoing_record = AccountBalance(account=outgoing_account, balance_description = balance_description, balance=new_outgoing_balance, balance_date=transfer_date)
             new_incoming_record.save()
             new_outgoing_record.save()
        else:
           #the transaction is in the past so you need to add a new balance and update all the other balances
           incoming_records_to_update = AccountBalance.objects.filter(balance_date__gte=transfer_date, balance_date__lte = now, account=incoming_account, account__user=self.request.user)
           outgoing_records_to_update = AccountBalance.objects.filter(balance_date__gte=transfer_date, balance_date__lte = now, account=outgoing_account, account__user=self.request.user)           
           print (incoming_records_to_update)
           print (outgoing_records_to_update)

           for record in incoming_records_to_update:
                record.balance = record.balance + transfer_amount
                record.save()   

           for record in outgoing_records_to_update:
                record.balance = record.balance - transfer_amount
                record.save()   
           latest_incoming_account = AccountBalance.objects.filter(balance_date__lt=transfer_date, account__user=self.request.user, account=incoming_account).order_by("-balance_date")[0]
           latest_outgoing_account = AccountBalance.objects.filter(balance_date__lt=transfer_date, account__user=self.request.user, account=outgoing_account).order_by("-balance_date")[0]
 
           print ('------in else---got the latest record in the past')
           print (latest_incoming_account)
           print (latest_outgoing_account)

           account_incoming_balance=latest_incoming_account.balance
           account_outgoing_balance = latest_outgoing_account.balance
           new_account_incoming_balance=transfer_amount + float(account_incoming_balance)    
           new_account_outgoing_balance=float(account_outgoing_balance) - transfer_amount     

           new_incoming_record = AccountBalance(account=incoming_account, balance_description = balance_description, balance= new_account_incoming_balance, balance_date=transfer_date)
           new_incoming_record.save() 


           new_outgoing_record = AccountBalance(account=outgoing_account, balance_description = balance_description, balance= new_account_outgoing_balance, balance_date=transfer_date)
           new_outgoing_record.save() 
             
       
        return super().form_valid(form)

class UpdateTransfer (LoginRequiredMixin, UpdateView):
    template_name = 'transfers/transfer_form.html'
    form_class = TransferForm
    success_url = reverse_lazy('transfers-index') 
    model = Transfer


    def form_valid(self, form):
        self.object = self.get_object()
        today = datetime.today()


        transfer_date = form.cleaned_data['transfer_date']
        transfer_amount = form.cleaned_data['transfer_amount']
        incoming_account = form.cleaned_data ['incoming_account']
        outgoing_account = form.cleaned_data ['outgoing_account']
        form.instance.user = self.request.user   
        print ('-------get-object')
        print (self.get_object())
        print (self.object.transfer_amount)
        print ('-----------------')
        amount_difference = self.object.transfer_amount - transfer_amount
        print ('difference:')
        print (amount_difference)
        transfer_date = form.cleaned_data['transfer_date']
        balance_incoming_records = AccountBalance.objects.filter(account__account_name=incoming_account, account__user = self.request.user, balance_date__range = [transfer_date, today]  )
        print (balance_incoming_records)
        for record in balance_incoming_records:
            record.balance = record.balance - amount_difference
            print (record.balance)
            record.save()

        balance_outgoing_records = AccountBalance.objects.filter(account__account_name=outgoing_account, account__user = self.request.user, balance_date__range = [transfer_date, today]  )
        print (balance_outgoing_records)
        for record in balance_outgoing_records:
            record.balance = record.balance + amount_difference
            print (record.balance)
            record.save()
        return super().form_valid(form)  

class DeleteTransfer (LoginRequiredMixin, DeleteView):
    model = Transfer
    form_class = TransferForm
    #success_url = reverse_lazy('transaction-index') 
    template_name = 'transfers/transfer_delete.html'
#    context_object_name = 'transaction'
    success_url = reverse_lazy('transfers-index')
    #fields ='__all__'


    def delete(self, *args, **kwargs):
        today = datetime.today()
        self.object = self.get_object()
        print (self.object)
        transfer_amount = self.object.transfer_amount
        print (transfer_amount)
        transfer_date = self.object.transfer_date
        incoming_account = self.object.incoming_account
        outgoing_account = self.object.outgoing_account

        incoming_account_record_to_delete = AccountBalance.objects.filter(balance_date=transfer_date, user = self.request.user, account=incoming_account).delete()
        outgoing_account_record_to_delete = AccountBalance.objects.filter(balance_date=transfer_date, user=self.request.user, account=outgoing_account).delete()

        incoming_records_to_update = AccountBalance.objects.filter(balance_date__gte=transfer_date, balance_date__lte = today, user=self.request.user, account=incoming_account)
        outgoing_records_to_update = AccountBalance.objects.filter(balance_date__gte=transfer_date, balance_date__lte = today, user=self.request.user, account=outgoing_account)


        for record in incoming_records_to_update:
            record.balance = record.balance - transfer_amount
            record.save()
        
        for record in outgoing_records_to_update:
            record.balance = record.balance + transfer_amount
            record.save()

        return super(DeleteTransfer, self).delete(*args, **kwargs)