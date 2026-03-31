from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib import messages
from django.conf import settings

from .forms import *

import json
import os
import subprocess
import uuid
# Create your views here.

def get_master_path():
    return os.path.join(settings.EXPORTS_DIR,'master.json')

def load_all_data():
    master_path = get_master_path()
    if not os.path.exists(master_path):
        return []
    try:
        with open(master_path,'r',encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError,IOError):
        return []
def save_all_data(data):
    master_path = get_master_path()
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_temp(sale_item,records):
    filename = f"temp_{uuid.uuid4().hex}.json"
    filepath = os.path.join(settings.EXPORTS_DIR, filename)
    data = {
        'total_records': records,      
        'new_record': sale_item              
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

def create_empty_temp():
    filename = f"temp_empty_{uuid.uuid4().hex}.json"
    filepath = os.path.join(settings.EXPORTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump([], f)  
    
    return filepath

def run_server(json_filepath):
    server_path = os.path.join(settings.BASE_DIR, 'server.py')
    if not os.path.exists(server_path):
        return False
    
    subprocess.Popen(
        ['python', server_path, json_filepath],
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

def index(request:HttpRequest):
    if request.method == 'POST':
        if 'clear_data' in request.POST:
            return clear_data(request)
        else:
            return add_sale(request)
    
    form = ProductForm()
    sales_data = load_all_data()
    context = {
        'title':'Обмен данными',
        'form':form,
        'sales_data':sales_data,
        'total_count':len(sales_data)
    }
    return render(request,'data_exchange/index.html',context)

def add_sale(request:HttpRequest):
    form = ProductForm(request.POST)
    if form.is_valid():
        sale_item = {
            'product_name': form.cleaned_data['name'],
            'product_group': dict(ProductForm.base_fields['category'].choices)[form.cleaned_data['category']],
            'quantity': float(form.cleaned_data['quantity']),
            'sale_price': float(form.cleaned_data['sale_price']),
            'purchase_price': float(form.cleaned_data['purchase_price']),
            'discount': float(form.cleaned_data['discount']),
        }
        sales_data = load_all_data()
        sales_data.append(sale_item)
        save_all_data(sales_data)
        total = len(sales_data)
        temp_filepath = create_temp(sale_item,total)
        run_server(temp_filepath)
        
        messages.success(request, f'✅ Товар "{sale_item["product_name"]}" добавлен')
    else:
        for field,errors in form.errors.items():
            for error in errors:
                messages.error(request, f'Ошибка в поле "{field}": {error}')

    return redirect('data_exchange:index')

def clear_data(request:HttpRequest):
    save_all_data([])
    messages.success(request, '🗑️ Все данные очищены')
    run_server(create_empty_temp())
    return redirect('data_exchange:index')
