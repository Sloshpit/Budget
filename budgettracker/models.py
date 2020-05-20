from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
class BudgetTracker(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_amount = models.FloatField()
    monthly_spend = models.FloatField(default=0)

    def __str__(self):
        return '%s  %s  %s %s ' %(self.date, self.category, self.budget_amount, self.id)
    

    def get_absolute_url(self):
        return reverse('budgettracker-index', args=[self.id])