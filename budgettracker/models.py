from django.db import models
from categories.models import Category
class BudgetTracker(models.Model):
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_amount = models.FloatField()
    def __str__(self):
        return '%s  %s  %s ' %(self.date, self.category, self.budget_amount)