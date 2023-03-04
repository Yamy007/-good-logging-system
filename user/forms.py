from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already")
        return email

class VerificationForm(forms.Form):
    verification_code = forms.CharField(max_length=6) 

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True)
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

class EmailVerificationForm(forms.Form):
    email = forms.EmailField(max_length=255, required=True)
