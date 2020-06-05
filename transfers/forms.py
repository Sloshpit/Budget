from django import forms
from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput, DateTimePickerInput
from django.forms import ModelForm
import datetime
from accounts.models import Account
from categories.models import Category
from .models import Transfer

class TransferForm(forms.ModelForm):

    class Meta:
        model = Transfer
        exclude = ('user',)
        widgets = {
            'transfer_date': DateTimePickerInput(format='%m/%d/%Y %H:%M:%S'), # default date-format %m/%d/%Y will be used
        }
    def __init__(self, *args, logged_user_id=None, **kwargs):
       super().__init__(*args, **kwargs)
       if logged_user_id is not None:
           self.fields['incoming_account'].queryset = Account.objects.filter(user=logged_user_id)        
           self.fields['outgoing_account'].queryset = Account.objects.filter(user=logged_user_id)        
