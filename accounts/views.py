from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.db.models import Sum
from .models import Account
from transactions.models import Transaction
from django.shortcuts import render
from .forms import GetDateForm

def index(request):
    template = loader.get_template('accounts/index.html')
    show_accounts = Account.objects.all()
    card_total_object = Account.objects.filter(account_type__contains="credit card").values('balance')
    card_total = card_total_object[0]['balance']
    other_account_total = Account.objects.exclude(account_type__contains="credit card").aggregate(sum=Sum('balance'))['sum'] or 0.00
    total = other_account_total - card_total
    context = {
        'show_accounts': show_accounts,
        'total': total    }
    return HttpResponse(template.render(context, request))

def detail(request, account_id):
    template = loader.get_template ('accounts/details.html')
    selected_account = Account.objects.filter(id=account_id).values('account_name')
    acct_name = selected_account[0]['account_name']
    trans_for_account_id = Transaction.objects.filter(account_name=1)
    transaction_total = Transaction.objects.filter(account_name=1).aggregate(sum=Sum('amount'))['sum'] or 0.00
    print (acct_name)
    context ={
        'acct_name': acct_name,
        'trans_for_account_id': trans_for_account_id,
        'transaction_total': transaction_total
    }
    return HttpResponse((template.render(context,request)))


def transactions_by_date(request):
    template = loader.get_template ('accounts/trans-by-date.html')
    startdate = 0
    enddate = 0
    if request.method == 'POST':
        form = GetDateForm(request.POST)
        if form.is_valid():
            #pass  # does nothing, just trigger the validation
             startdate = form.cleaned_data['startdate']
             enddate = form.cleaned_data ['enddate']
             trans_for_account_id = Transaction.objects.filter(trans_date__range=[startdate,enddate])
             print (trans_for_account_id)
             context ={
                'trans_for_account_id': trans_for_account_id,
                }
             return HttpResponse((template.render(context,request)))
    else:
        form = GetDateForm()
    return render(request, 'accounts/trans-by-date.html', {'form': form})