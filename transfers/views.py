from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from .models import Transfer


def index(request):
    template = loader.get_template('transfers/index.html')
    show_transfers = Transfer.objects.all()

    context = {
        'show_transfers': show_transfers,
    }
    return HttpResponse(template.render(context, request))
    