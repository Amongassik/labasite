from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label="Наименование товара",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название товара'})
    )
    category = forms.ChoiceField(
        choices=[
            ('electronics', 'Электроника'),
            ('accessories', 'Аксессуары'),
            ('furniture', 'Мебель'),
        ],
        label="Группа товара",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField( 
        min_value=1,
        label="Проданное количество",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'})
    )
    sale_price = forms.DecimalField( 
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label="Продажная цена",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    purchase_price = forms.DecimalField(  
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label="Закупочная цена",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    discount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        initial=0,
        label="Скидка (%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

class EditSaleForm(forms.Form):
    index = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(max_length=255)
    category = forms.ChoiceField(choices=ProductForm.base_fields['category'].choices)
    quantity = forms.IntegerField(min_value=1)
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    purchase_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    discount = forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)



    