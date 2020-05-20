from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Sum, Max
from .models import BudgetTracker
from transactions.models import Transaction
from accounts.models import Account, AccountBalance
from transfers.models import Transfer
from .forms import GetDateForm
from django.shortcuts import render
from datetime import datetime, timedelta, date
import calendar
from calendar import monthrange
from .forms import CreateBudget
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

@login_required

def get_cat_budget(request):
    category = request.GET.get('category')
    thedate = request.GET.get('thedate')
 
    #today = datetime.today()
    #print (today)
    thedate = datetime.strptime(thedate, '%m/%d/%Y')
    first = thedate.replace(day=1)
    last_day_last_month = first - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)

    start_date = (first_day_last_month.year, first_day_last_month.month, first_day_last_month.day)
    start_date= str(start_date[0]) +"-"+ str(start_date[1]) +"-"+ str(start_date[2])

    end_date = (last_day_last_month.year, last_day_last_month.month, last_day_last_month.day)
    end_date = str(end_date[0]) +"-"+ str(end_date[1]) +"-"+ str(end_date[2])
    #work on this tomorrow
    #get last month's budget and subtract any transactions that happend on that budget to show what's left
    previous_budget = BudgetTracker.objects.filter(id=category, date__range=[start_date, end_date]).values('budget_amount')
    previous_budget = previous_budget[0]  
    print (previous_budget)
    return JsonResponse({'data':previous_budget})
@login_required
def index(request):
    template = loader.get_template ('budgettracker/index.html')
    personal_budget_array =[]
    today = str(date.today())
    if request.method == 'POST':
        form = GetDateForm(request.POST)
        if form.is_valid():
             form.fields['start_month'].label = "View budget for:"        

            #get the start and end date to pull all budget items from the model
             start_month = form.cleaned_data['start_month']
             convert_month = datetime.strftime(start_month, '%b %Y')
             num_days = monthrange(start_month.year, start_month.month)
             
             enddate = (start_month.year, start_month.month, num_days[1])
             end_year = str(enddate[0])
             end_month = str(enddate[1])
             end_day = str(enddate[2])
             enddate = end_year+"-"+ end_month+ "-" + end_day
             
             first_day = (start_month.year, start_month.month, 1)
             start_year = str(first_day[0])
             start_mnth = str(first_day[1])
             start_day = str(first_day[2])
             budget_month = start_month.strftime("%b %Y")
             startdate = start_year+"-"+ start_mnth+ "-" + start_day
             budgets_for_selected_month = BudgetTracker.objects.filter(date__range=[startdate,enddate])
             print (budgets_for_selected_month)
             budget_total =  BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
             total_spend =  BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00
             account_names = Account.objects.filter(user=request.user).values('account_name').distinct()
             #calculate money left to budget:transactions with initial spend + income records (exclude initial )
             total_account_balance = 0
             for acct_name in account_names:
                latest_account_balance = AccountBalance.objects.filter(account__account_name=acct_name['account_name'], account__user=request.user).latest('balance_date')
                total_account_balance = total_account_balance + latest_account_balance.balance
            #    total_account_balance = total_account_balance + float(latest_account_balance['balance'])
             initial_balance = Transaction.objects.filter(trans_date__range=[startdate,enddate], category__category="Initial Balance", user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
             income = Transaction.objects.filter(trans_date__range=[startdate,enddate], amount__gte=0).exclude(category__category="Initial Balance", user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
             total_left = float(initial_balance) + float(budget_total)
             #get all refund/income transactions
             total_budget_left = float(initial_balance) + float(income) - float(budget_total)
             total_monthly_spend = BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user)
             print (total_monthly_spend)
             total_monthly_budget_left = budget_total + total_spend
             print ('-------total money left in budget')
             print (total_monthly_budget_left)
             total_monthly_budget_percentage = (total_spend/budget_total)*-100
             form = GetDateForm()   
             form.fields['start_month'].label = "View budget for:"        
             context= {
              'form': form, 
              'budgets_for_selected_month': budgets_for_selected_month,
              'total_spend' : total_spend, 
              'total_left': total_left,
              'budget_total': budget_total, 
              'budget_month_date' : budget_month,
              'total_budget_left' : total_budget_left,
              'total_monthly_budget_left': total_monthly_budget_left,
              'total_monthly_budget_percentage': total_monthly_budget_percentage,
             }
            # return HttpResponse((template.render(context,request)))
             return render(request, 'budgettracker/index.html',context)
    else:
        today = datetime.today()
        num_days = monthrange(today.year, today.month)
        enddate = (str(today.year)+"-"+str(today.month)+"-"+ str(num_days[1]))
        startdate = (str(today.year) +"-" +str(today.month)+"-"+str(1))
        budgets_for_selected_month = BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user)
        budget_total =  BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00

        total_spend =  BudgetTracker.objects.filter(date__range=[startdate,enddate]).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00
        account_names = Account.objects.filter(user=request.user).values('account_name').distinct()
        print (account_names)
             #calculate money left to budget:transactions with initial spend + income records (exclude initial )
        total_account_balance = 0
        for acct_name in account_names:
            latest_account_balance = AccountBalance.objects.filter(account__account_name=acct_name['account_name'], account__user=request.user).latest('balance_date')
            total_account_balance = total_account_balance + latest_account_balance.balance
            initial_balance = Transaction.objects.filter(trans_date__range=[startdate,enddate], category__category="Initial Balance", user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
            income = Transaction.objects.filter(trans_date__range=[startdate,enddate], amount__gte=0).exclude(category__category="Initial Balance", user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
            total_left = float(initial_balance) + float(budget_total)
             #get all refund/income transactions

        total_budget_left = float(initial_balance) + float(income) - float(budget_total)
        total_monthly_budget_left = budget_total + total_spend
        total_monthly_budget_percentage = (total_spend/budget_total)*-100

        print ('-------total money left in budget')
        print (total_monthly_budget_left)
        form = GetDateForm()
        form.fields['start_month'].label = "View budget for:"        
        budget_month = today.strftime("%b %Y")
        context= {
            'form': form, 
            'budgets_for_selected_month': budgets_for_selected_month,
            'total_spend' : total_spend, 
            'total_left': total_left,
            'budget_total': budget_total, 
            'budget_month_date' : budget_month,
            'total_budget_left' : total_budget_left,
            'total_monthly_budget_left': total_monthly_budget_left,
            'total_monthly_budget_percentage': total_monthly_budget_percentage,
        }
    return render(request, 'budgettracker/index.html',context)


class BudgettrackerCreate (LoginRequiredMixin, CreateView):

     template_name = 'budgettracker/budgettracker_form.html'
     form_class = CreateBudget
     success_url = reverse_lazy('budgettracker-index') 
     model = BudgetTracker
    #fields = '__all__'
     def form_valid(self, form):
        date = form.cleaned_data['date']
        print (type(date))
        category = form.cleaned_data['category']
        budget_amount = form.cleaned_data['budget_amount']
        form.instance.user = self.request.user
        self.object = form.save()  

        next_month_date = date + relativedelta(months=1)
        next_month = BudgetTracker(date=next_month_date, category=category, budget_amount=budget_amount, user=self.request.user)
        next_month.save()
        return super().form_valid(form)


class BudgettrackerUpdate (LoginRequiredMixin, UpdateView):
    template_name = 'budgettracker/budgettracker_form.html'
    form_class = CreateBudget
    success_url = reverse_lazy('budgettracker-index') 
    #form = CreateTransactionForm
    #success_url = reverse_lazy ('transaction-index')
    model = BudgetTracker
    #fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']

class BudgettrackerDelete (LoginRequiredMixin, DeleteView):
    model = BudgetTracker
    form_class = CreateBudget
    #success_url = reverse_lazy('transaction-index') 
    template_name = 'budgettracker/budgettracker_delete.html'
 #   context_object_name = 'budgettracker'
    success_url = reverse_lazy('budgettracker-index')
    #fields ='__all__'