from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from accounts.models import Account, AccountBalance
from accounthistory.models import AccountHistory
from .models import Transfer
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import TransferForm
from django.urls import reverse_lazy
from datetime import datetime
from django.utils import timezone
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
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(logged_user_id=self.request.user.id)
        return kwargs

    def form_valid(self, form):
        now = datetime.today()
        now_string = now.strftime('%Y-%m-%d %H:%M:%S')
        transfer_date = form.cleaned_data['transfer_date']
        transfer_amount = form.cleaned_data['transfer_amount']
        incoming_account = form.cleaned_data ['incoming_account']
        outgoing_account = form.cleaned_data ['outgoing_account']
        form.instance.user = self.request.user   
        print (self.request.user.id)
        print (incoming_account)
        self.object = form.save()
        now = datetime.today()
        print (transfer_date)
        transfer_date_no_time = transfer_date.date()
        balance_description = "Account Transfer from "+str(incoming_account) +" "+ "To " +str(outgoing_account)
        #if there is an INCOMING account balance for the transfer date
        if AccountBalance.objects.filter(account__account_name=incoming_account, account__user=self.request.user.id, balance_date=transfer_date.date()).exists():
            print ('accunt balance exists for this date on incoming')
            #get the accountbalance values to update
            incoming_account_values = AccountBalance.objects.filter(account__account_name=incoming_account, account__user=self.request.user.id, balance_date=transfer_date.date()).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
 
            #calculate the new balance
            incoming_account_balance=incoming_account_values['balance']
            new_incoming_balance=transfer_amount + float(incoming_account_balance)
            print ('------new incoming balance in if------')
            print (new_incoming_balance)
            #grab any future account balance records to update
            incoming_account_records_to_update = AccountBalance.objects.filter(balance_date__gt=transfer_date_no_time, balance_date__lte = now.date(), account=incoming_account, account__user=self.request.user.id)
            for record in incoming_account_records_to_update:
                record.balance = record.balance + transfer_amount
                record.save()   
            #create a new account history incoming record

            incoming_new_account_history_record = AccountHistory( user = self.request.user, account = incoming_account, transfer=self.object, transaction = None, date=transfer_date, balance = new_incoming_balance)
            incoming_new_account_history_record.save()             
            incoming_account_update = AccountBalance.objects.filter(account=incoming_account, account__user=self.request.user.id).update(balance = new_incoming_balance)  
 
            # update any future account history incoming record
            incoming_new_acct_records_to_update = AccountHistory.objects.filter(account=incoming_account, user=self.request.user, date__gt=transfer_date, date__lte = now)
            print (incoming_new_acct_records_to_update)
            for record in incoming_new_acct_records_to_update:
                record.balance = record.balance + transfer_amount
                record.save()   
        #Incoming account record DOES NOT exist for date
        else:
            #get the latest balance on file
            latest_incoming_account = AccountBalance.objects.filter(account=incoming_account, account__user=self.request.user.id, balance_date__lte=transfer_date.date()).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
            print ('latest incoming account')
            print (latest_incoming_account)
            
            #calculate the new balance
            incoming_account_balance=latest_incoming_account['balance']
            new_incoming_balance=transfer_amount + float(incoming_account_balance)

            new_incoming_record = AccountBalance(account=incoming_account, balance_description = balance_description, balance=new_incoming_balance, balance_date=transfer_date.date())

            #grab any future account balance records to update
            incoming_account_records_to_update = AccountBalance.objects.filter(balance_date__gt=transfer_date.date(), balance_date__lte = now.date(), account=incoming_account, account__user=self.request.user.id)
            for record in incoming_account_records_to_update:
                record.balance = record.balance + transfer_amount
                record.save()   
            #create a new account history record
            incoming_new_account_history_record = AccountHistory( user = self.request.user, account = incoming_account, transfer=self.object, transaction = None, date=transfer_date, balance = new_incoming_balance)
            incoming_new_account_history_record.save()             
            incoming_account_update = AccountBalance.objects.filter(account=incoming_account, account__user=self.request.user.id).update(balance = new_incoming_balance)  
 
            # update any future account history incoming record
            incoming_new_acct_records_to_update = AccountHistory.objects.filter(account=incoming_account, user=self.request.user, date__gt=transfer_date, date__lte = now)
            print (incoming_new_acct_records_to_update)
            for record in incoming_new_acct_records_to_update:
                record.balance = record.balance + transfer_amount
                print (record.balance)
                record.save()   
        
        #if OUTGOING account exists for current date
        if AccountBalance.objects.filter(account__account_name=outgoing_account, account__user=self.request.user.id, balance_date=transfer_date.date()).exists():
            print ('accunt balance exists for this date on incoming')
            #get the accountbalance values to update
            outgoing_account_values = AccountBalance.objects.filter(account__account_name=outgoing_account, account__user=self.request.user.id, balance_date=transfer_date.date()).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
 
            #calculate the new balance
            outgoing_account_balance=outgoing_account_values['balance']
         #   new_outgoing_balance=transfer_amount + float(outgoing_account_balance)
            new_outgoing_balance=float(outgoing_account_balance) - transfer_amount 

 
            #grab any future account balance records to update
            outgoing_account_records_to_update = AccountBalance.objects.filter(balance_date__gt=transfer_date_no_time, balance_date__lte = now.date(), account=outgoing_account, account__user=self.request.user.id)
            for record in outgoing_account_records_to_update:
                record.balance = record.balance - transfer_amount
                record.save()   
            #create a new account history incoming record

            outgoing_new_account_history_record = AccountHistory( user = self.request.user, account = outgoing_account, transfer=self.object, transaction = None, date=transfer_date, balance = new_outgoing_balance)
            outgoing_new_account_history_record.save()             
            outgoing_account_update = AccountBalance.objects.filter(account=outgoing_account, account__user=self.request.user.id).update(balance = new_outgoing_balance)  
 
            # update any future account history incoming record
            outgoing_new_acct_records_to_update = AccountHistory.objects.filter(account=outgoing_account, user=self.request.user, date__gt=transfer_date, date__lte = now)

            for record in outgoing_new_acct_records_to_update:
                record.balance = record.balance - transfer_amount
                record.save()                     
        else:
            #get the latest balance on file
            latest_outgoing_account = AccountBalance.objects.filter(account=outgoing_account, account__user=self.request.user.id, balance_date__lte=transfer_date.date()).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
            
            #calculate the new balance
            outgoing_account_balance=latest_outgoing_account['balance']
            new_outgoing_balance=float(outgoing_account_balance) - transfer_amount 

            new_outgoing_record = AccountBalance(account=outgoing_account, balance_description = balance_description, balance=new_outgoing_balance, balance_date=transfer_date.date())

            #grab any future account balance records to update
            outgoing_account_records_to_update = AccountBalance.objects.filter(balance_date__gt=transfer_date.date(), balance_date__lte = now.date(), account=outgoing_account, account__user=self.request.user.id)
            for record in outgoing_account_records_to_update:
                record.balance = record.balance - transfer_amount
                record.save()   
            #create a new account history record
            outgoing_new_account_history_record = AccountHistory( user = self.request.user, account = outgoing_account, transfer=self.object, transaction = None, date=transfer_date, balance = new_outgoing_balance)
            outgoing_new_account_history_record.save()             
            outgoing_account_update = AccountBalance.objects.filter(account=outgoing_account, account__user=self.request.user.id).update(balance = new_outgoing_balance)  
 
            # update any future account history outgoing record
            outgoing_new_acct_records_to_update = AccountHistory.objects.filter(account=outgoing_account, user=self.request.user, date__gt=transfer_date, date__lte = now)

            for record in outgoing_new_acct_records_to_update:
                record.balance = record.balance - transfer_amount
                record.save()   



        return super().form_valid(form)


class UpdateTransfer (LoginRequiredMixin, UpdateView):
    template_name = 'transfers/transfer_form.html'
    form_class = TransferForm
    success_url = reverse_lazy('transfers-index') 
    model = Transfer
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(logged_user_id=self.request.user.id)
        return kwargs

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
        balance_incoming_records = AccountBalance.objects.filter(account__account_name=incoming_account, account__user = self.request.user, balance_date__range = [transfer_date.date(), today]  )
        print (balance_incoming_records)
        for record in balance_incoming_records:
            record.balance = record.balance - amount_difference
            print (record.balance)
            record.save()

        balance_outgoing_records = AccountBalance.objects.filter(account__account_name=outgoing_account, account__user = self.request.user, balance_date__range = [transfer_date.date(), today]  )
        print (balance_outgoing_records)
        for record in balance_outgoing_records:
            record.balance = record.balance + amount_difference
            print (record.balance)
            record.save()

        incoming_new_account_history_record = AccountHistory.objects.filter( user = self.request.user, account = incoming_account, date__range=[transfer_date, today])
        for record in incoming_new_account_history_record:
            record.balance = record.balance - amount_difference
            print (record.balance)
            record.save()


        outgoing_new_account_history_record = AccountHistory.objects.filter( user = self.request.user, account = outgoing_account, date__range=[transfer_date, today])
        for record in outgoing_new_account_history_record:
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
        #get account for each based on date
        incoming_account_description = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user,account=incoming_account)
        outgoing_account_description = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=outgoing_account)
        print (incoming_account_description[0].balance_description)
        print (outgoing_account_description[0].balance_description)
        if incoming_account_description[0].balance_description == 'initial':
            print ('update the account amount rather that deleting')
            incoming_account_record_to_update = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=incoming_account)
            print (incoming_account_record_to_update[0].balance)
            new_balance = incoming_account_record_to_update[0].balance - transfer_amount
            incoming_account_record_to_update.balance = new_balance
            incoming_account_record_to_update = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=incoming_account).update(balance=new_balance)

        else:
            incoming_account_record_to_delete = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=incoming_account).delete()

        if outgoing_account_description[0].balance_description == 'initial':
            outgoing_account_record_to_update = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=outgoing_account)
            new_balance = outgoing_account_record_to_update[0].balance + transfer_amount
            outgoing_account_record_to_update.balance = new_balance
            outgoing_account_record_to_update = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=outgoing_account).update(balance=new_balance)

        else:
            outgoing_account_record_to_delete = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=outgoing_account).delete()

      #      outgoing_account_record_to_delete = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=outgoing_account).delete()
      #      incoming_historyaccount_record_to_delete = AccountHistory.objects.filter(date=transfer_date, account__user=self.request.user, account=incoming_account).delete()

   #         outgoing_account_record_to_delete = AccountBalance.objects.filter(balance_date=transfer_date.date(), account__user=self.request.user, account=outgoing_account).delete()
            incoming_historyaccount_record_to_delete = AccountHistory.objects.filter(date=transfer_date, account__user=self.request.user, account=incoming_account).delete()
            outgoing_historyaccount_record_to_delete = AccountHistory.objects.filter(date=transfer_date, account__user=self.request.user, account=outgoing_account).delete()


        incoming_records_to_update = AccountBalance.objects.filter(balance_date__gt=transfer_date.date(), balance_date__lte = today.date(), account__user=self.request.user, account=incoming_account)
        outgoing_records_to_update = AccountBalance.objects.filter(balance_date__gt=transfer_date.date(), balance_date__lte = today.date(), account__user=self.request.user, account=outgoing_account)

        for record in incoming_records_to_update:
            record.balance = record.balance - transfer_amount
            record.save()
        
        for record in outgoing_records_to_update:
            record.balance = record.balance + transfer_amount
            record.save()

        incoming_historyrecords_to_update = AccountHistory.objects.filter(date__gt=transfer_date, date__lte = today, account__user=self.request.user, account=incoming_account)
        outgoing_historyrecords_to_update = AccountHistory.objects.filter(date__gt=transfer_date, date__lte = today, account__user=self.request.user, account=outgoing_account)

        for record in incoming_historyrecords_to_update:
            record.balance = record.balance - transfer_amount
            record.save()
        
        for record in outgoing_historyrecords_to_update:
            record.balance = record.balance + transfer_amount
            record.save()

        return super(DeleteTransfer, self).delete(*args, **kwargs)