from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
class BudgetTracker(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_amount = models.FloatField()
    monthly_spend = models.FloatField(default=0)
    class Meta:
        ordering = ["category"]
    def __str__(self):
        return '%s  %s  %s %s %s ' %(self.date, self.category, self.budget_amount, self.id, self.monthly_spend)
    

    def get_absolute_url(self):
        return reverse('budgettracker-index', args=[self.id])

class BudgetLeft (models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    amount = models.FloatField()
    def __str__(self):
        return '%s  %s ' %(self.amount, self.user)
