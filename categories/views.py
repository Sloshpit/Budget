from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from transactions.models import Transaction
from .models import Category


def index(request):
    template = loader.get_template('categories/index.html')
    show_categories = Category.objects.all()
    show_transactions = Transaction.objects.all()
    total = Transaction.objects.all().aggregate(sum=Sum('amount'))['sum'] or 0.00
    total = "{:.2f}".format(total)

    context = {
        'show_categories': show_categories,
        'show_transactions':show_transactions,
        'total': total,
    }
    return HttpResponse(template.render(context, request))
    