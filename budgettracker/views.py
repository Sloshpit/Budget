from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Sum
from .models import BudgetTracker
from .forms import GetDateForm
from django.shortcuts import render
from datetime import datetime, timedelta
from calendar import monthrange
from transactions.models import Transaction
from accounts.models import Account
from transfers.models import Transfer
from .forms import CreateBudget
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

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

def index(request):
    template = loader.get_template ('budgettracker/index.html')

    personal_budget_array =[]
    if request.method == 'POST':
        form = GetDateForm(request.POST)
        if form.is_valid():
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
             
             startdate = start_year+"-"+ start_mnth+ "-" + start_day

             budgets_for_selected_month= BudgetTracker.objects.filter(date__range=[startdate,enddate]).exclude(category=28)
             #get all the transactions for each budgettracker item
             for budget in budgets_for_selected_month:
                 #category_transactions = Transaction.objects.filter(category=budget.category)
                 category_transactions_spend = Transaction.objects.filter(category=budget.category, trans_date__range = [startdate, enddate]).aggregate(sum=Sum('amount'))['sum'] or 0.00
                 personal_budget_array.append((budget.category, budget.budget_amount, category_transactions_spend))

             budget_total = BudgetTracker.objects.filter(date__range=[startdate, enddate]).exclude(category=28).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
             budget_total = "{:.2f}".format(budget_total)            
             budget_month_date = datetime.strftime(start_month, '%b %Y')
           
             total_spend = 0
           
             for personal_budget in personal_budget_array:
                 total_spend = total_spend + personal_budget[2]
             total_budget_left = float(budget_total) + float(total_spend)
           
             context ={
                'budgets_for_selected_month': budgets_for_selected_month,
                'budget_total':budget_total,
                'budget_month_date':budget_month_date,
                'form': form,
                'personal_budget_array': personal_budget_array,
                'total_spend': total_spend,
                'total_budget_left': total_budget_left
                }
             return HttpResponse((template.render(context,request)))
    else:
        form = GetDateForm()
    return render(request, 'budgettracker/index.html', {'form': form})


class BudgettrackerCreate (CreateView):

     template_name = 'budgettracker/budgettracker_form.html'
     form_class = CreateBudget
     success_url = reverse_lazy('budgettracker-add') 
     model = BudgetTracker
    #fields = '__all__'

class BudgettrackerUpdate (UpdateView):
    template_name = 'budgetTracker/budgettracker_form.html'
    form_class = CreateBudget
    success_url = reverse_lazy('budgettracker-index') 
    #form = CreateTransactionForm
    #success_url = reverse_lazy ('transaction-index')
    model = BudgetTracker
    #fields = ['store', 'description', 'amount','trans_date', 'category', 'account_name']

class BudgettrackerDelete (DeleteView):
    model = BudgetTracker
    form_class = CreateBudget
    #success_url = reverse_lazy('transaction-index') 
    template_name = 'budgettracker/budgettracker_delete.html'
    context_object_name = 'budgettracker'
    success_url = reverse_lazy('budgettracker-index')
    #fields ='__all__'