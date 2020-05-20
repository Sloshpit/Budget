from django import forms
from django.forms import ModelForm
import datetime

from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude =('user',)
