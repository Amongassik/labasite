from django import forms
from django.contrib.auth.hashers import check_password
from .models import Emploees,Logins

class LoginForm(forms.Form):
    login = forms.CharField(
        label='Логин',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')

        if login and password:
            try:
                user = Logins.objects.get(login=login)
                if not user.check_password(password):
                    raise forms.ValidationError("Неверный пароль")
                cleaned_data['user'] = user
            except Logins.DoesNotExist:
                raise forms.ValidationError('Пользователь с таким логином не найден')
        return cleaned_data