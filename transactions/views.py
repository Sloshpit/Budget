from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template import loader
from django.db.models import Sum
from .models import Transaction
from budgettracker.models import BudgetTracker
from categories.models import Category
from accounts.models import Account,AccountBalance
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .forms import CreateTransactionForm, UpdateTransactionForm
from django.shortcuts import render, redirect, reverse
from datetime import datetime, date, timedelta
from calendar import monthrange
import calendar
from budgets.budgets.common import get_first_of_month, get_last_of_month, get_first_of_next_month
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required


def index(request):
    template = loader.get_template('transactions/index.html')
    today = datetime.today()
    enddate = get_last_of_month (today)
    startdate = get_first_of_month(today)
    show_transactions = Transaction.objects.filter(user=request.user)
    total = Transaction.objects.filter(trans_date__range=[startdate, enddate], user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
    total = "{:.2f}".format(total)

    context = {
        'show_transactions':show_transactions,
        'total': total,
    }
    return HttpResponse(template.render(context, request))

class TransactionCreate (LoginRequiredMixin, CreateView):

     template_name = 'transactions/transaction_form.html'
     form_class = CreateTransactionForm
     success_url = reverse_lazy('transaction-index') 
     model = Transaction

     def form_valid(self, form):
        now = datetime.today()
        print ('now.date')
        print (now)
        store = form.cleaned_data ['store']
        category = form.cleaned_data ['category']
        acct_name = form.cleaned_data['account_name']
        print('account name: '+ str(acct_name))
        amount = form.cleaned_data['amount']
        trans_date = form.cleaned_data['trans_date']
        form.instance.user = self.request.user   
        user_id = self.request.user.id
        self.object = form.save()

     #   bud_date = str(trans_date.year) +"-" +str(trans_date.month) + "-"+ "1"
        bud_date = get_first_of_month(trans_date)
        #create a category budget for a transaction if it does not exist
        if not BudgetTracker.objects.filter(date=bud_date, user=self.object.user).exists():
            print ('inside no category exists for transaction')
            bud_amount = amount
            if amount < 0:
                bud_amount = bud_amount *-1
            new_budget = BudgetTracker(category=category, budget_amount = bud_amount, monthly_spend = '0', date = bud_date, user=self.object.user)
            new_budget.save()
        # get the latest account balance based on the transaction date.  This should account for a present record and going into the past.

        #latest_account = AccountBalance.objects.filter(account__account_name=acct_name).values('account__account_name', 'balance', 'balance_date').latest('balance_date')
        latest_account = AccountBalance.objects.filter(account__account_name = acct_name, balance_date__lte=trans_date, account__user=self.object.user).values('account__account_name', 'balance', 'balance_date').order_by("-balance_date")[0]
        print (latest_account)
        print('--------latest acount----')
        latest_account_date = latest_account['balance_date']
        print (latest_account_date.date())

        if latest_account_date.date() == trans_date:
            #just update the existing balance if a balance exists for date the transaction is suppsoed to 
            new_balance = latest_account['balance'] + amount
            print ('new balance:')
            print (new_balance)
            update_account = AccountBalance.objects.filter(account__account_name = acct_name, balance_date__lte=trans_date, account__user=self.object.user).update(balance = new_balance)
            print ('update')
            print (update_account)
            records_to_update = AccountBalance.objects.filter(account__account_name=acct_name, account__user=user_id, balance_date__gt=trans_date, balance_date__lte = now.date())
            print ('records to update:')
            print (records_to_update)
        #update all potential future record balances
            for record in records_to_update:
                record.balance = record.balance + amount
                record.save() 

        else:
        #create a new balance record if one doesn't exist for that date
            balance_description = str(store) +" "+ str(category)
            new_account_balance=amount + float(latest_account['balance'])        
            new_record = AccountBalance(account=acct_name, balance_description = balance_description, balance=new_account_balance, balance_date=trans_date)
            new_record.save()
            records_to_update = AccountBalance.objects.filter(account__account_name=acct_name, account__user=self.object.user,balance_date__gt=trans_date, balance_date__lte = now.date())
            print (records_to_update)
        #update any potential future records
            for record in records_to_update:
                record.balance = record.balance + amount
                record.save() 


        first_of_month = get_first_of_month(trans_date)

        next_first_of_month = get_first_of_next_month(trans_date)
 #get all transactions for this month, get the budget for the category, do the math on that category
        transaction_spend = Transaction.objects.filter(category__category = category, trans_date__range = [first_of_month, trans_date], user=self.object.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
        print ('transaction spend so far:')
        print (transaction_spend)
        category_budget = BudgetTracker.objects.filter(category__category = category, date__range = [first_of_month, trans_date], user=self.object.user)

        #category_spend = budget_amount - transaction_spend
        print ('cagegory_budget no user')
        print (category_budget)           
        for spend in category_budget:
             print ('inside loop------------')
             print (spend.monthly_spend)
             spend.monthly_spend = transaction_spend
             print (spend.monthly_spend)
             spend.save()
        category_budget = BudgetTracker.objects.filter(category__category = category, date = next_first_of_month, user=self.object.user)
        print ('category_budget next month:')
        print (category_budget)
        for budget in category_budget:
            print (budget.budget_amount)
            budget.budget_amount =  budget.budget_amount + transaction_spend
            budget.save()               
        return super().form_valid(form)

    #fields = '__all__'

class TransactionUpdate (LoginRequiredMixin, UpdateView):
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
        amount_difference = amount - self.object.amount
        trans_date = form.cleaned_data['trans_date']
        self.object = form.save()

        balance_records = AccountBalance.objects.filter(account__account_name=acct_name, balance_date__range = [trans_date, today], user=self.user.object )
        for record in balance_records:
            record.balance = record.balance + amount_difference
            record.save()
   #get all transactions for this month, get the budget for the category, do the math on that category      
        first_of_month = get_first_of_month(trans_date)
        next_first_of_month = get_first_of_next_month(trans_date)
        transaction_spend = Transaction.objects.filter(category__category = category, trans_date__range = [first_of_month, trans_date], user=self.user.object).aggregate(sum=Sum('amount'))['sum'] or 0.00

        category_budget = BudgetTracker.objects.filter(category__category = category, date__range = [first_of_month, trans_date], user=self.user.object)
        category_budget_next_month = BudgetTracker.objects.filter(category__category = category, date = next_first_of_month, user=self.user.object)

        #category_spend = budget_amount - transaction_spend
  
        for spend in category_budget:
             spend.monthly_spend = transaction_spend
             spend.save()
             for budget in category_budget_next_month:
                 print (spend.budget_amount)
                 print (budget.budget_amount)
                 budget.budget_amount = spend.budget_amount + transaction_spend
                 print (budget.budget_amount)
                 budget.save()


       # for budget in category_budget:
       #     budget.budget_amount =  budget.budget_amount + transaction_spend
       #     budget.save()        

        return super().form_valid(form)

class TransactionDelete (LoginRequiredMixin, DeleteView):
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
        category = self.object.category
        print ('user!!')
        user = self.object.user
        account_record_to_delete = AccountBalance.objects.filter(balance_date=trans_date, account=acct_name).delete()
        records_to_update = AccountBalance.objects.filter(account=acct_name, balance_date__gte=trans_date, balance_date__lte = today)
        for record in records_to_update:
            record.balance = record.balance - amount
            record.save()
   #get all transactions for this month, get the budget for the category, do the math on that category      
        first_of_month = get_first_of_month(trans_date)
        next_first_of_month = get_first_of_next_month(trans_date)
        transaction_spend = Transaction.objects.filter(category__category = category, trans_date__range = [first_of_month, trans_date], user=user).aggregate(sum=Sum('amount'))['sum'] or 0.00

        category_budget = BudgetTracker.objects.filter(category__category = category, date__range = [first_of_month, trans_date], user=user)
        category_budget_next_month = BudgetTracker.objects.filter(category__category = category, date = next_first_of_month, user=user)

        #category_spend = budget_amount - transaction_spend
  
        for spend in category_budget:
             spend.monthly_spend = spend.monthly_spend - amount
             spend.save()
             for budget in category_budget_next_month:
                 budget.budget_amount = budget.budget_amount - amount
                 budget.save()

        return super(TransactionDelete, self).delete(*args, **kwargs)

class TransactionList (LoginRequiredMixin, ListView): 
    template_name = 'transactions/index.html'
    form_class = CreateTransactionForm
    success_url = reverse_lazy ('transaction-index')
    model = Transaction
    context_object_name = 'show_transactions'
    fields ='__all__'

def get_account (request):
    print ('inside get account')
    account = request.GET.get('account', None)
    the_date = AccountBalance.objects.filter(account__id=account, account__user=request.user).values('balance_date').order_by('-balance_date').last()
    formatted_date = (str(the_date['balance_date'].month) +'-'+str(the_date['balance_date'].day)+'-'+str(the_date['balance_date'].year))
    data = {
        'date': formatted_date
    }
    return JsonResponse(data)

def category_details (request,categoryid):
        template = loader.get_template('transactions/category_transactions.html')
        today = datetime.today()
        first_of_month = get_first_of_month(today)
        last_of_month = get_last_of_month(today)
        transactions = Transaction.objects.filter(category=categoryid,trans_date__range=[first_of_month,last_of_month], user=request.user)
        total =  Transaction.objects.filter(category=categoryid,trans_date__range=[first_of_month,last_of_month], user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
        category = Category.objects.filter (id=categoryid, user=request.user)
        print (category)
        category_budget = BudgetTracker.objects.filter(category__category = category[0], date__range = [first_of_month, last_of_month], user=request.user)
        print (category_budget)
        #category_total = BudgetTracker.objects.filter(category=category_name[0])
        context = {
            'transactions': transactions,
            'total': total,
        }
        return HttpResponse(template.render(context, request))
