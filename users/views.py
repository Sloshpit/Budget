from categories.models import Category
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView, PasswordChangeDoneView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.contrib.auth.models import User

# Create your views here.

class RegisterView(FormView):
	template_name = 'users/register.html'
	success_url = ("/users/login")
	form_class = RegisterForm
	def form_valid(self, form):
		username = form.cleaned_data['username']
		password1 = form.cleaned_data['password1']
		password2 = form.cleaned_data['password2']
		email = form.cleaned_data['email']
		user=form.save()
		initial_balance_category = Category(user = user, master_category='Initial Balance', category='Initial Balance')
		initial_balance_category.save()
		income_category = Category (user = user, master_category = 'Income', category = 'Income' )
		income_category.save()		
		return super().form_valid(form)

class LoginView (LoginView):
	template_name = 'users/login.html'
	success_url = ("/accounts")

class PasswordResetView (PasswordResetView):
	template_name = 'users/password_reset_form.html'

class PasswordChangeView (PasswordChangeView):
	template_name = 'users/password_change_form.html'
class PasswordChangeDoneView (PasswordChangeDoneView):
	template_name = 'users/password_change_done.html'

class PasswordResetDoneView (PasswordResetDoneView):
	template_name = 'users/password_reset_done.html'

class PasswordResetConfirmView(PasswordResetConfirmView):
	template_name = 'users/password_reset_confirm_form.html'

class PasswordResetCompleteView(PasswordResetCompleteView):
	template_name = 'users/password_reset_complete.html'
