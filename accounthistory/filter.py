
import django_filters
from .models import AccountHistory
from accounts.models import Account
from django import forms
from django.contrib.auth.models import User, Group
class AccountFilter (django_filters.FilterSet):
    account =  django_filters.ModelMultipleChoiceFilter(queryset=Account.objects.all(),widget=forms.CheckboxSelectMultiple, label="")
    class Meta:
        model = AccountHistory
        fields = ['account',]
#    def get_filterset_kwargs(self, **kwargs):
 #       user = kwargs.pop['user']
 #       print (user)

  #  @property
  #  def qs(self):
  #      parent = super(AccountFilter, self).qs
  #      request = get_current_user()
  #      print (request.id)
        #print (parent.filter('account'))
  #      return parent.filter(user = request.id)