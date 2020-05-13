from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
from django import forms
import datetime
from .models import BudgetTracker
class GetDateForm(forms.Form):
    start_month = forms.DateField(
        widget=
        MonthPickerInput(format='%Y-%m'), initial=datetime.date.today(), input_formats=["%Y-%m"]
    )
    
# validation datefield

class CreateBudget(forms.ModelForm):

    class Meta:
        model = BudgetTracker
        fields ='__all__'
        widgets = {
            'date': MonthPickerInput(), # default date-format %m/%d/%Y will be used
        }
