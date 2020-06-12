from django import forms
import datetime
from accounts.models import Account
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
class AccountDropdown(forms.Form):
    accounts = Account.objects.all()
    accounts = forms.CharField(label="choose an account", widget=forms.Select(choices=accounts))


