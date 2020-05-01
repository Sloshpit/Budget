from django.db import models
from django.forms import ModelForm
from accounts.models import Account, AccountBalance

class Transfer(models.Model):
    transfer_amount = models.FloatField()
    transfer_date = models.DateField()
   #add a category as a foreign key later that pulls this in as a dropdown
    incoming_account = models.ForeignKey(AccountBalance, on_delete=models.CASCADE, related_name = 'incoming_account')
    outgoing_account = models.ForeignKey(AccountBalance, on_delete=models.CASCADE)



    def get_absolute_url(self):
        return reverse('transfers-index', args=[self.id])
    
    def __str__(self):
        return '%s  %s  %s %s ' %(self.transfer_amount, self.transfer_date, self.incoming_account, self.outgoing_account)