from django import forms
from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
from django.forms import ModelForm
import datetime
from accounts.models import Account
from categories.models import Category
from .models import Transaction

class CreateTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields ='__all__'
        widgets = {
            'trans_date': DatePickerInput(), # default date-format %m/%d/%Y will be used
        }
