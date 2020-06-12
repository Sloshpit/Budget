from django import forms
from django.forms import ModelForm
import datetime
from django.utils.safestring import mark_safe
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude =('user',)
    def __init__(self, *args, **kwargs):
       self.user = kwargs.pop('user')
       super().__init__(*args, **kwargs)

    def clean (self):
         user = self.user
         cleaned_data = super().clean()
         master_category = cleaned_data['master_category']
         category = cleaned_data['category']  
         carry_over = cleaned_data['carry_over']
         savings_or_investment = cleaned_data['savings_or_investment']         
         check = Category.objects.filter( user=self.user, category = category)
         if Category.objects.filter(user=self.user, category = category).exists():
            raise forms.ValidationError(
    ((mark_safe('<div class="alert alert-danger text-center" role="alert">A '+ str(category)+' category exists. '+'. <a href="/categories/'+str(check[0].id)+'/update">Update category?</a></div>')))
 )


class UpdateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude =('user',)
    def __init__(self, *args, **kwargs):
       self.user = kwargs.pop('user')
       super().__init__(*args, **kwargs)

    def clean (self):
         user = self.user
         cleaned_data = super().clean()
         master_category = cleaned_data['master_category']
         category = cleaned_data['category']  
         carry_over = cleaned_data['carry_over']
         savings_or_investment = cleaned_data['savings_or_investment']
#         check = Category.objects.filter( user=self.user, category = category)
 #        if Category.objects.filter(user=self.user, category = category).exists():
  #          raise forms.ValidationError(
   # ((mark_safe('<div class="alert alert-danger text-center" role="alert">A '+ str(category)+' category exists. '+'. <a href="/categories/'+str(check[0].id)+'/update">Update category?</a></div>')))
 #)