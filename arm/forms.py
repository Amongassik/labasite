from django import forms
from .models import Product,Client

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock_qty']
        labels = {
            'name': 'Название товара',
            'price': 'Цена',
            'stock_qty': 'Количество на складе',
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'total_purchases', 'current_balance', 'credit_limit', 'current_debt', 'comment']
        labels = {
            'name': 'Имя клиента',
            'total_purchases': 'Общий счет покупок',
            'current_balance': 'Текущий счет',
            'credit_limit': 'Потолок кредита',
            'current_debt': 'Текущий долг',
            'comment': 'Комментарий',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }