from django import forms
from django.contrib.auth.hashers import check_password
from .models import Emploees,Logins
import random

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
    
class EmployeeForm(forms.ModelForm):
    
    class Meta:
        model = Emploees
        fields = ['last_name', 'first_name', 'patronymic', 'position', 'address', 'phone']
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'position': 'Должность',
            'address': 'Адрес',
            'phone': 'Телефон',        
        }
        widgets = {
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'patronymic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество (необязательно)'
            }),
            'position': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите адрес'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите телефон'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patronymic'].required = False
        
    @staticmethod
    def generate_login(last_name, first_name):
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }

        def transliterate(text:str):
            text = text.lower()
            result = ''
            for char in text:
                if char in translit_dict:
                    result+=translit_dict[char]
                elif char.isalpha():
                    result+=char
                else:
                    result+=''
            return result
        last_translit = transliterate(last_name)
        first_translit =transliterate(first_name)

        login = f"{last_translit}{first_translit}"
        orig_login = login
        counter = 1
        while Logins.objects.filter(login=login).exists():
            login = f"{orig_login}{counter}"
            counter+=1
        return login
    
    @staticmethod
    def generate_password():
        return f"{random.randint(1000,9999)}"
    
    def save(self,commit=True):
        employee = super().save(commit=commit)
        login = None
        password = None
        if commit:
            login = self.generate_login(employee.last_name, employee.first_name)
            password = self.generate_password()
            user_account = Logins(
                employee = employee,
                login = login
            )
            user_account.set_password(password)
            user_account.save()
        return employee,login,password
