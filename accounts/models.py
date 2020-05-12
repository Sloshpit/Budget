from django.db import models

class Account(models.Model):
    account_name = models.CharField (max_length = 200)
    account_type = models.CharField (max_length = 200)
    initial_balance = models.FloatField()
    date = models.DateTimeField()
    
    def get_absolute_url(self):
        return reverse('accounts-index', args=[self.id])

    def __str__(self):
       return '%s' %(self.account_name)


class AccountBalance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance_description = models.CharField(max_length=200)
    balance = models.FloatField()
    balance_date = models.DateTimeField()

    def get_absolute_url(self):
        return reverse('accounts-index', args=[self.id])
        
    def __str__(self):
         return '%s %s %s' % (self.account, self.balance, self.balance_date)    
    
