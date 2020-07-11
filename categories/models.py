from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    master_category = models.CharField(max_length=200, default='none')
    category = models.CharField(max_length=200)
    carry_over = models.BooleanField (default=False)
    savings_or_investment = models.BooleanField (default=False)

    class Meta:
        ordering = ["category"]
    def __str__(self):
        return self.category
    def get_absolute_url(self):
        return reverse('categories-index', args=[self.id])