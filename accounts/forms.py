from django import forms
from bootstrap_datepicker_plus import DatePickerInput

class GetDateForm(forms.Form):

    startdate = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y')
    )
    enddate = forms.DateField(
        widget=DatePickerInput(format='%m/%d/%Y')
    )