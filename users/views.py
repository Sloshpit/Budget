# views.py
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView


# Create your views here.

class RegisterView(CreateView):
	template_name = 'users/register.html'
	success_url = ("/users/login")
	form_class = RegisterForm
	def is_valid (self, form):
		form.save()
		return super (CreateUser, self).form.valid(form)

class LoginView (LoginView):
	template_name = 'users/login.html'
	success_url = ("/accounts")
