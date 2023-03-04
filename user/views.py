from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .forms import RegistrationForm, VerificationForm, LoginForm, EmailVerificationForm
from django.contrib.auth.decorators import login_required
import random

from django.contrib.auth.decorators import user_passes_test

def anonymous_required(function=None, redirect_url=None):
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=redirect_url, 
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@anonymous_required(redirect_url='<your-page>') # if user is logged in, redirect to <your-page> page
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            login(request, user) # !! user is not active yet !!

            verification_code = generate_verification_code()
            request.session['verification_code'] = verification_code

            send_verification_code(user.email, verification_code)

            return redirect('/verification/')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})



def verification(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            try:
                entered_code = form.cleaned_data['verification_code'] if len(form.cleaned_data['verification_code']) == 6 else form.cleaned_data['verification_code'].split('-')[0]+form.cleaned_data['verification_code'].split('-')[1]
            except:
                entered_code = form.cleaned_data['verification_code']
            stored_code = request.session.get('verification_code')
            if entered_code == stored_code:
                user_id = request.session.get('_auth_user_id')
               
                if user_id is not None:
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        pass
                    else:
                        user.is_active = True
                        user.save()
                        login(request, user)
                        del request.session['verification_code']
                        return redirect('home')
            messages.error(request, 'Invalid verification code')
        else:
            print("form is not valid")   
    else:
        
        form = VerificationForm()
        
        # Check if user has completed registration and verification process
        if request.session.get('verification_code') is None:
            return redirect('register')
        elif request.session.get('_auth_user_id') is None:
            return redirect('login')

    return render(request, 'verification.html', {'form': form})


@anonymous_required(redirect_url='<your-page>') # if user is logged in, redirect to <your-page> page
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email/phone or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_code(email_or_phone, code):
    # send verification code here via email or SMS, for example:
    send_mail(
        'Verification code',
        f'Your verification code is {code}',
        settings.EMAIL_HOST_USER,
        [email_or_phone],
        fail_silently=False,
    )
