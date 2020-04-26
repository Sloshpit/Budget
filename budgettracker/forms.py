from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
from django import forms
import datetime
class GetDateForm(forms.Form):
    start_month = forms.DateField(
        widget=
        MonthPickerInput(format='%Y-%m'), initial=datetime.date.today(), input_formats=["%Y-%m"]
    )
# validation datefield
    