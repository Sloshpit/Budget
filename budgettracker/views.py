from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from .models import BudgetTracker
from .forms import GetDateForm
from django.shortcuts import render
from datetime import datetime
from calendar import monthrange


def index(request):
    template = loader.get_template ('budgettracker/index.html')
    start_month = 0
    enddate = 0
    if request.method == 'POST':
        form = GetDateForm(request.POST)
        if form.is_valid():
            #get the start and end date to pull all budget items from the model
             start_month = form.cleaned_data['start_month']

             num_days = monthrange(start_month.year, start_month.month)
             
             enddate = (start_month.year, start_month.month, num_days[1])
             end_year = str(enddate[0])
             end_month = str(enddate[1])
             end_day = str(enddate[2])
             enddate = end_year+"-"+ end_month+ "-" + end_day
             
             first_day = (start_month.year, start_month.month, 1)
             start_year = str(first_day[0])
             start_month = str(first_day[1])
             start_day = str(first_day[2])
             
             startdate = start_year+"-"+ start_month+ "-" + start_day

             budgets_for_selected_month= BudgetTracker.objects.filter(date__range=[startdate,enddate])
             budget_total = BudgetTracker.objects.filter(date__range=[startdate, enddate]).aggregate(sum=Sum('budget_amount'))['sum'] or 0.00
             budget_total = "{:.2f}".format(budget_total)            
             
             budget_month_date = start_month + "/" +start_year

             context ={
                'budgets_for_selected_month': budgets_for_selected_month,
                'budget_total':budget_total,
                'budget_month_date':budget_month_date
                }
             return HttpResponse((template.render(context,request)))
    else:
        form = GetDateForm()
    return render(request, 'budgettracker/index.html', {'form': form})