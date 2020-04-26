from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from .models import Transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView


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