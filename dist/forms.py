from django import forms
from .models import Emploees,Logins

class LoginForm(forms.ModelForm):
    class Meta:
        model = Logins
        fields = '__all__'