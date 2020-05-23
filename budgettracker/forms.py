from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
from django import forms
import datetime
from .models import BudgetTracker
from categories.models import Category
from django.contrib.auth.models import User
class GetDateForm(forms.Form):
    start_month = forms.DateField(
        widget=
        MonthPickerInput(format='%Y-%m'), initial=datetime.date.today(), input_formats=["%Y-%m"]
    )
    
# validation datefield

class CreateBudget(forms.ModelForm):
    class Meta:
        model = BudgetTracker
        exclude =('user',)
        #fields='__all__'
        widgets = {
            'date': MonthPickerInput(), # default date-format %m/%d/%Y will be used
        }
  
    def __init__(self, *args, logged_user_id=None, **kwargs):
       super().__init__(*args, **kwargs)
       if logged_user_id is not None:
           print (logged_user_id)
           self.fields['category'].queryset = Category.objects.filter(
               user=logged_user_id
           )
           print (self.fields['category'].queryset)
         

