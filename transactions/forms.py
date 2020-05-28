from django import forms
from bootstrap_datepicker_plus import DatePickerInput, MonthPickerInput
from django.forms import ModelForm
import datetime
from accounts.models import Account
from categories.models import Category
from .models import Transaction

class CreateTransactionForm(forms.ModelForm):
    CHOICES = [('spend', 'Spend'), ('income', 'Income/Refund')]
    transaction_type = forms.ChoiceField(
        choices = CHOICES, # this is optional
        widget = forms.RadioSelect,
        initial ='spend'
    )
    class Meta:
        model = Transaction
        fields =('store','description','transaction_type','category','amount', 'account_name', 'trans_date')
        widgets = {
            'trans_date': DatePickerInput(format='%m/%d/%Y').start_of('transaction days'), # default date-format %m/%d/%Y will be used
        }
    def __init__(self, *args, logged_user_id=None, **kwargs):
       super().__init__(*args, **kwargs)
       if logged_user_id is not None:
           self.fields['category'].queryset = Category.objects.filter(user=logged_user_id)
           self.fields['account_name'].queryset = Account.objects.filter(user=logged_user_id)        
    def clean_amount(self):
       for field, value in self.cleaned_data.items():
            amount = self.cleaned_data['amount']

       if self.cleaned_data['transaction_type']=='spend':
               amount = amount *-1
 
       return amount
    
    def clean_trans_date(self):
        trans_date = self.cleaned_data['trans_date']
        return trans_date
        
    def clean_description(self):
        description =  self.cleaned_data ['description']
        return description

    def clean_store(self):
        store = self.cleaned_data['store']
        return store

    def clean_account_name(self):
        account_name = self.cleaned_data ['account_name']
        return (account_name)

    def clean_category(self):
        category = self.cleaned_data ['category']
        return (category)



class UpdateTransactionForm(forms.ModelForm):
    CHOICES = [('spend', 'Spend'), ('income', 'Income/Refund')]
    transaction_type = forms.ChoiceField(
        choices = CHOICES, # this is optional
        widget = forms.RadioSelect,
        initial ='spend'
    )
    class Meta:
        model = Transaction
        fields =('account_name','store','description','category','transaction_type','amount', 'trans_date')
        widgets = {
            'trans_date': DatePickerInput(), # default date-format %m/%d/%Y will be used
        }


    def __init__(self, *args, logged_user_id=None, **kwargs):
       super().__init__(*args, **kwargs)
       if logged_user_id is not None:
           self.fields['category'].queryset = Category.objects.filter(user=logged_user_id)
           self.fields['account_name'].queryset = Account.objects.filter(user=logged_user_id)        

    def clean_trans_date(self):
        trans_date = self.cleaned_data['trans_date']
        return trans_date
    
    def clean_amount(self):

       for field, value in self.cleaned_data.items():
           if self.cleaned_data['transaction_type']=='spend':
               amount = self.cleaned_data['amount'] *-1
       return amount
        
    def clean_description(self):
        description =  self.cleaned_data ['description']
        return description

    def clean_store(self):
        store = self.cleaned_data['store']
        return store

    def clean_account_name(self):
        account_name = self.cleaned_data ['account_name']
        return (account_name)

    def clean_category(self):
        category = self.cleaned_data ['category']
        return (category)
        