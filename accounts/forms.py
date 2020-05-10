from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from django.forms import ModelForm
from .models import Account, AccountBalance

class GetDateForm(forms.Form):

    startdate = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y')
    )
    enddate = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y')
    )


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields ='__all__'
