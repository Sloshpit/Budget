from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
from django import forms
import datetime
from .models import BudgetTracker
from categories.models import Category
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
class GetDateForm(forms.Form):
    start_month = forms.DateField(
        widget=
        MonthPickerInput(format='%Y-%m'), initial=datetime.date.today(), input_formats=["%Y-%m"])
    
# validation datefield

class CreateBudget(forms.ModelForm):
    class Meta:
        model = BudgetTracker
        exclude =('user','monthly_spend')
        #fields='__all__'
        widgets = {
            'date': MonthPickerInput().start_of('2020-10-01'), # default date-format %m/%d/%Y will be used
        }
  
    def __init__(self, *args, logged_user_id=None, **kwargs):
       self.user = kwargs.pop('user')
       super().__init__(*args, **kwargs)

       if logged_user_id is not None:
           print (logged_user_id)
           self.fields['category'].queryset = Category.objects.filter(
               user=logged_user_id
           )

    def clean (self):
         user = self.user
         cleaned_data = super().clean()
         date = cleaned_data['date']
         category = cleaned_data['category']
         budget_amount = cleaned_data['budget_amount']
         check = BudgetTracker.objects.filter( user=self.user, date=date, category__category = category)

         if BudgetTracker.objects.filter(user=self.user, date=date, category__category = category).exists():
            raise forms.ValidationError(
    ((mark_safe('<div class="alert alert-danger text-center" role="alert">A budget already exist for'+ str(category)+'for '+ str(date.month) +'-'+ str(date.day)+ '. <a href="/budgettracker/'+str(check[0].id)+'/update">Update budget?</a></div>')))
 )

class UpdateBudget(forms.ModelForm):
    class Meta:
        model = BudgetTracker
        exclude =('user','monthly_spend')
        #fields='__all__'
        widgets = {
            'date': MonthPickerInput(), # default date-format %m/%d/%Y will be used
        }
  
    def __init__(self, *args, **kwargs):
       self.user = kwargs.pop('user')
       super().__init__(*args, **kwargs)


    def clean (self):
         user = self.user
         cleaned_data = super().clean()
         date = cleaned_data['date']
         category = cleaned_data['category']
         budget_amount = cleaned_data['budget_amount']
