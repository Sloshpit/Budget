from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Sum, Max, Avg, F, Exists,Q
from .models import BudgetTracker
from transactions.models import Transaction
from accounts.models import Account, AccountBalance
from transfers.models import Transfer
from categories.models import Category
from .forms import GetDateForm
from django.shortcuts import render
from datetime import datetime, timedelta, date
import calendar
from calendar import monthrange
from .forms import CreateBudget, UpdateBudget
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from budgets.budgets.common import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

from django_tables2 import SingleTableView
from .tables import BudgetTable

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

def get_monthly_budget (start_month, request):
    print (start_month)
    convert_month = datetime.strftime(start_month, '%b %Y')
    num_days = monthrange(start_month.year, start_month.month)
    exclude_list = ['Initial Balance', 'Income']             
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

    first_of_month = get_first_of_month(start_month)
    last_of_month = get_last_of_month(start_month)
    first_of_last_month = get_first_of_last_month(start_month)
    last_of_last_month = get_last_of_last_month(start_month)
    first_of_next_month = get_first_of_next_month(start_month)

    b_f_month = BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).exclude(category__category=exclude_list)
    b_f_last_month = BudgetTracker.objects.filter(date__range=[first_of_last_month,last_of_last_month], user=request.user).exclude(category__category=exclude_list)

    b_f_next_month_carryover = BudgetTracker.objects.filter (date = first_of_next_month, user=request.user, category__carry_over = True).exclude(category__category=exclude_list)
    b_f_month_carryover = BudgetTracker.objects.filter (date = first_of_month, user=request.user, category__carry_over = True).exclude(category__category=exclude_list)

    for budget in b_f_month_carryover:
        record_found = False
        for bud in b_f_next_month_carryover:
                if budget.category == bud.category:
                    record_found = True

        if not record_found:
            BudgetTracker.objects.create(date= first_of_next_month, user=request.user, category=budget.category, budget_amount = budget.budget_amount, monthly_spend = 0)

    budgets_for_selected_month = b_f_month.annotate(total_left=(F('budget_amount')+F('monthly_spend')), carryover = (F('category__carry_over')), total_percent_left = ((F('monthly_spend')+F('budget_amount'))/F('budget_amount'))*100).order_by('-budget_amount')

    budget_list = []


    for budget in budgets_for_selected_month:
        last_month_spend = 0
        for bud in b_f_last_month:

                if budget.category == bud.category:
                    last_month_spend = bud.monthly_spend
                else:
                    latst_month_spend = 0    
        budget_list.append([budget.category, budget.budget_amount, budget.monthly_spend, budget.total_left, budget.carryover, budget.total_percent_left, last_month_spend, budget.id])
        last_month_spend = 0
   # budgets_for_selected_month = BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).exclude(category__category=exclude_list).annotate(total_left=(F('budget_amount')+F('monthly_spend'))).order_by('-budget_amount')
    budget_total =  BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
    total_spend =  BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00

    account_names = Account.objects.filter(user=request.user).values('account_name').distinct()

    total_account_balance = 0
    for acct_name in account_names:
        latest_account_balance = AccountBalance.objects.filter(account__account_name=acct_name['account_name'], account__user=request.user).latest('balance_date')
        total_account_balance = total_account_balance + latest_account_balance.balance

    #    get the initial balance for each record in the given month.
    initial_balance = Transaction.objects.filter(trans_date__range=[startdate,enddate], category__category="Initial Balance", user=request.user).aggregate(sum=Sum('amount'))['sum'] or 0.00
    income = Transaction.objects.filter(trans_date__range=[startdate,enddate], user=request.user, category__category="Income").aggregate(sum=Sum('amount'))['sum'] or 0.00

    total_left = float(initial_balance) + float(budget_total)

    #get all refund/income transactions
    first_of_month = get_first_of_month(start_month)
    last_of_month = get_last_of_month(start_month)
    first_of_last_month = get_first_of_last_month(start_month)
    last_of_last_month = get_last_of_last_month(start_month)
    first_of_next_month = get_first_of_next_month(start_month)

    template = loader.get_template ('budgettracker/index.html')
    #transaction and income from last month
    transaction_income_prev_month = Transaction.objects.filter(category__category='Income', user=request.user, trans_date__range=[first_of_last_month, last_of_last_month]).aggregate(sum=Sum('amount'))['sum'] or 0.00
    transaction_initial_balance_prev_month = Transaction.objects.filter(category__category='Initial Balance', user=request.user, trans_date__range=[first_of_last_month, last_of_last_month]).aggregate(sum=Sum('amount'))['sum'] or 0.00
    #money left from last month (budget - spend)

    
    budget_last_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_last_month, last_of_last_month]).exclude(category__category = exclude_list).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00

    budget_this_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_month, last_of_month]).exclude(category__category = exclude_list).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
    budget_spend_last_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_last_month, last_of_last_month]).exclude(category__category = exclude_list).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00   
    #income for this month
    transaction_income_this_month = Transaction.objects.filter(category__category = 'Income', user=request.user, trans_date__range=[first_of_month, last_of_month]).aggregate(sum=Sum('amount'))['sum'] or 0.00
    transaction_initial_balance_this_month = Transaction.objects.filter( category__category = 'Initial Balance', user=request.user, trans_date__range=[first_of_month,last_of_month]).aggregate(sum=Sum('amount'))['sum'] or 0.00
    #carry over money left
    non_carry_over_budget_last_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_last_month, last_of_last_month]).exclude(category__category = exclude_list).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
    non_carry_over_budget_spend_last_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_last_month, last_of_last_month]).exclude(category__category = exclude_list).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00    
    
    #calculate how much budget there is for this month:

    #budget_left = transaction_income_prev_month + transaction_initial_balance_prev_month-(budget_last_month - budget_spend_last_month) + transaction_income_this_month + transaction_initial_balance_this_month - budget_this_month
    #budget_left = transaction_income_this_month+transaction_initial_balance_this_month - budget_this_month + transaction_income_prev_month + transaction_initial_balance_prev_month + (budget_last_month - budget_spend_last_month)
    budget_left_this_month = transaction_income_this_month + transaction_initial_balance_this_month - budget_this_month
    budget_left_from_last_month = transaction_income_prev_month +transaction_initial_balance_prev_month + budget_spend_last_month
    print (first_of_last_month)
    print (last_of_last_month)
    money_left_from_last_month = Transaction.objects.filter( user=request.user, trans_date__range=[first_of_last_month, last_of_last_month]).aggregate(sum=Sum('amount'))['sum'] or 0.00

    total_budget_left = budget_left_this_month + budget_left_from_last_month

    # total_budget_left = float(initial_balance) + float(income) - float(total_spend)-float(budget_total)
    total_monthly_spend = BudgetTracker.objects.filter(date__range=[startdate,enddate], user=request.user)

    #savings_investment_budget = BudgetTracker.objects.filter (date_range=[startdate, enddate],user=request.user, category__category__savings_or_investment=True)
    savings_amount = 0
    sav_inv_categories = Category.objects.filter(savings_or_investment=True)
    for category in sav_inv_categories:
        savings_amount = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_month, last_of_month]).filter(category__category = category).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00 + savings_amount
    #get the transaction amounts that could be savings from this month:

    transactions_savings_investments = Transaction.objects.filter(category__savings_or_investment=True, user=request.user, trans_date__range=[first_of_month, last_of_month]).aggregate(sum=Sum('amount'))['sum'] or 0.00
  
    total_monthly_budget_left = budget_total + total_spend - savings_amount - transactions_savings_investments

    current_savings = savings_amount + transactions_savings_investments
    print (total_spend)
    print ('total spend---')
    print (savings_amount)
    print (budget_total)
    if total_spend < 0:
        total_monthly_budget_percentage = (total_spend/(budget_total-savings_amount))*-100
    else:
        total_monthly_budget_percentage = 0
        
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
    'current_savings' : current_savings,
    'b_f_last_month' : b_f_last_month,
    'budget_list' : budget_list,
    }
    return (context)



@login_required
def index(request):
 template = loader.get_template ('budgettracker/index.html')
 personal_budget_array =[]
 today = str(date.today())
 record_count= BudgetTracker.objects.filter(user=request.user).count()
 if record_count > 0 :   
    if request.method == 'POST':
        form = GetDateForm(request.POST)
        if form.is_valid():
             print ('--------If form is valid pass in june-------')
             form.fields['start_month'].label = "View budget for:"        

            #get the start and end date to pull all budget items from the model
             start_month = form.cleaned_data['start_month']
             print (start_month)
             context = get_monthly_budget (start_month, request)
            # return HttpResponse((template.render(context,request)))
             return render(request, 'budgettracker/index.html',context)
    else:
        print ('inside else of post------------')
        today = datetime.today()
        context = get_monthly_budget (today, request)
    return render(request, 'budgettracker/index.html',context)
 else:
     context={}
     return render (request, 'budgettracker/index.html', context)

class BudgettrackerCreate (LoginRequiredMixin, CreateView):

     template_name = 'budgettracker/budgettracker_form.html'
     form_class = CreateBudget
     success_url = reverse_lazy('budgettracker-index') 
     model = BudgetTracker
     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(logged_user_id=self.request.user.id, user = self.request.user.id)
        return kwargs
    #fields = '__all__'
     def form_valid(self, form):
        date = form.cleaned_data['date']
        print (type(date))
        category = form.cleaned_data['category']
        budget_amount = form.cleaned_data['budget_amount']
#        if BudgetTracker.objects.filter(user=self.request.user, date=date, category__category = category).exists():
#            raise form.ValidationError("You already have a budget item for this category in this month")
        form.instance.user = self.request.user
        self.object = form.save()  


        check_carryover = Category.objects.filter(category=category, user=self.request.user)
        for check in check_carryover:
            carry_over = check.carry_over
        if carry_over== True:
            next_month_date = date + relativedelta(months=1)
            next_month = BudgetTracker(date=next_month_date, category=category, budget_amount=budget_amount, user=self.request.user)
            next_month.save()
        return super().form_valid(form)


class BudgettrackerUpdate (LoginRequiredMixin, UpdateView):
    template_name = 'budgettracker/budgettracker_form.html'
    form_class = UpdateBudget
    success_url = reverse_lazy('budgettracker-index') 
    #form = CreateTransactionForm
    #success_url = reverse_lazy ('transaction-index')
    model = BudgetTracker
    #fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user = self.request.user.id)
        return kwargs
    def form_valid (self,form):
        category = form.cleaned_data['category']
        date = form.cleaned_data['date']
        budget_amount = form.cleaned_data['budget_amount']
        old_object = form.instance
        form.save()
 
        check_carryover = Category.objects.filter(category=category, user=self.request.user)
        for check in check_carryover:
            carry_over = check.carry_over
        if carry_over== True:
            this_month_spend = BudgetTracker.objects.filter(date=date, category=category, user=self.request.user)
            print ('-----this month spend')
            for spend in this_month_spend:
              current_month_spend = spend.monthly_spend
 
            next_month_date = date + relativedelta(months=1)
            future_budgets = BudgetTracker.objects.filter (date__gte=date, category=category, user=self.request.user)
            for budget in future_budgets:

                budget_left = budget.budget_amount - budget_amount
                budget.budget_amount = budget.budget_amount - budget_left + current_month_spend
                budget.save()
          #  next_month = BudgetTracker(date=next_month_date, category=category, budget_amount=budget_amount, user=self.request.user)
          #  next_month.save()

        return super().form_valid(form)
       
class BudgettrackerDelete (LoginRequiredMixin, DeleteView):
    model = BudgetTracker
    form_class = CreateBudget
    #success_url = reverse_lazy('transaction-index') 
    template_name = 'budgettracker/budgettracker_delete.html'
 #   context_object_name = 'budgettracker'
    success_url = reverse_lazy('budgettracker-index')
    #fields ='__all__'

def get_budget_average (request):
    print ('inside get budget average')
    category = request.GET.get('category', None)
    print (category)
    date = request.GET.get ('date', None)
    print (date)
    the_date = datetime.strptime(date,'%Y-%m-%d')
    startdate=get_first_of_three_months_ago(the_date)
    enddate=get_last_of_last_month(the_date)
    print (startdate)
    print (enddate)
    #add stuff to make it 3 month average
    category_average_spend = BudgetTracker.objects.filter (category__category = category, date__range=[startdate,enddate], user=request.user).values('monthly_spend').aggregate(Avg('monthly_spend'))
    category_average_budget = BudgetTracker.objects.filter (category__category = category, date__range=[startdate,enddate], user=request.user).values('budget_amount').aggregate(Avg('budget_amount'))
    print (category_average_spend)
  #  the_date = AccountBalance.objects.filter(account__id=account, account__user=request.user).values('balance_date').order_by('-balance_date').last()
  #  formatted_date = (str(the_date['balance_date'].month) +'-'+str(the_date['balance_date'].day)+'-'+str(the_date['balance_date'].year))
    data = {
        'category_average_spend': category_average_spend,
        'category_average_budget': category_average_budget
    }
    return JsonResponse(data)


class BudgetListView (SingleTableView):
    model = BudgetTracker
    table_class = BudgetTable
    template_name='budgettracker/budget-list.html'

def budget_list (request):
    table=BudgetTable(BudgetTracker.objects.filter(user=request.user, date='2020-05-01').annotate(total_left=(F('budget_amount')+F('monthly_spend'))).order_by('-budget_amount'))
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    return render(request, 'budgettracker/budget-list.html',{
        "table":table
    })

def test (request):
    today = date.today()
    first_of_month = get_first_of_month(today)
    last_of_month = get_last_of_month(today)
    first_of_last_month = get_first_of_last_month(today)
    last_of_last_month = get_last_of_last_month(today)
    
    first_of_next_month = get_first_of_next_month(today)
    template = loader.get_template ('budgettracker/index.html')
    transaction_income = Transaction.objects.filter(amount__gte=0, category__category = 'Income', user=request.user, trans_date__range=[first_of_next_month, '2020-06-30']).aggregate(sum=Sum('amount'))['sum'] or 0.00
    transaction_initial_balance = Transaction.objects.filter(amount__gte=0, category__category = 'Initial Balance', user=request.user, trans_date__range=[first_of_next_month, '2020-06-30']).aggregate(sum=Sum('amount'))['sum'] or 0.00
    exclude_list = ['Initial Balance', 'Income']
    budget_last_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_month, last_of_month], category__carry_over = True).exclude(category__category = exclude_list).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
    budget_spend_last_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_month, last_of_month], category__carry_over = True).exclude(category__category = exclude_list).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00   
    budget_this_month =  BudgetTracker.objects.filter(user=request.user, date__range=[first_of_next_month, '2020-06-30']).exclude(category__category = exclude_list).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
    budget_spend_this_month = BudgetTracker.objects.filter(user=request.user, date__range=[first_of_next_month, '2020-06-30']).exclude(category__category = exclude_list).aggregate(sum=Sum('monthly_spend'))['sum'] or 0.00   
    last_month_budget_left = float(budget_last_month) - float(budget_spend_last_month)

    money_left_to_budget = float(transaction_income)+float(transaction_initial_balance)+last_month_budget_left-budget_this_month
    print (budget_last_month)
    print (budget_spend_last_month)
    print (budget_this_month)
    print (budget_spend_this_month)
    print (money_left_to_budget)
    context ={
        'transaction_income':transaction_income,
    }
    return render(request, 'budgettracker/index.html',context)    