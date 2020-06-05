from django.db import models
from django.forms import ModelForm
from accounts.models import Account, AccountBalance
from django.contrib.auth.models import User
class Transfer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE )
    transfer_amount = models.FloatField()
    transfer_date = models.DateTimeField()
   #add a category as a foreign key later that pulls this in as a dropdown
    incoming_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name = 'incoming_account')
    outgoing_account = models.ForeignKey(Account, on_delete=models.CASCADE)



    def get_absolute_url(self):
        return reverse('transfers-index', args=[self.id])
    
    def __str__(self):
        return '%s  %s  %s %s ' %(self.transfer_amount, self.transfer_date, self.incoming_account, self.outgoing_account)