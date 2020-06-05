
from django.db import models
from django.forms import ModelForm
from accounts.models import Account
from django.contrib.auth.models import User
from transactions.models import Transaction
from transfers.models import Transfer
class AccountHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default = 1) 
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE , null=True)
    transfer = models.ForeignKey (Transfer, on_delete = models.CASCADE, null=True)
    date = models.DateTimeField()
    balance = models.FloatField()

    def __str__(self):
         return '%s %s %s %s %s %s' % (self.user, self.account, self.transaction, self.transfer, self.balance, self.date)    