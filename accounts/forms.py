from django import forms
from bootstrap_datepicker_plus import DateTimePickerInput
from django.forms import ModelForm
from .models import Account, AccountBalance

class GetDateForm(forms.Form):

    startdate = forms.DateTimeField(
        widget=DateTimePickerInput(format='%m/%d/%Y')
    )
    enddate = forms.DateTimeField(
        widget=DateTimePickerInput(format='%m/%d/%Y')
    )


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account

        fields ='__all__'
        widgets = {
            'date': DateTimePickerInput(), # default date-format %m/%d/%Y will be used
        }
