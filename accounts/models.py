from django.db import models
class Account(models.Model):
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=200)
    balance = models.FloatField()
    balance_date = models.DateField()
    def __str__(self):
         return '%s' % (self.account_name)
    