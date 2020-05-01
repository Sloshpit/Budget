from django.contrib import admin

from .models import Account, AccountBalance
admin.site.register(Account)
admin.site.register(AccountBalance)
