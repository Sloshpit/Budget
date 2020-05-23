from django.contrib import admin

from .models import BudgetTracker, BudgetLeft
admin.site.register(BudgetTracker)
admin.site.register(BudgetLeft)