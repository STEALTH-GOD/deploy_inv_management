from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.


def register(request):
    """Registration disabled - only admin can create user accounts"""
    messages.warning(request, 'Registration is disabled. Please contact the administrator for account creation.')
    return redirect('login') 

def login_view(request):
    if request.method=='POST':
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user =form.get_user()
            login(request,user)
            return redirect('home')
    else: 
        form=AuthenticationForm()
    return render(request,'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
    
        
