from django import forms
from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
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
            'transfer_date': DatePickerInput(), # default date-format %m/%d/%Y will be used
        }
