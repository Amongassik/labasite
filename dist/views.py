from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from .forms import LoginForm, EmployeeForm
from .models import Logins, Emploees


def index(request: HttpRequest):
    if not request.session.get('is_authenticated', False):
        request.session['is_guest'] = True
        request.session['is_authenticated'] = False
        is_guest = True
        is_authenticated = False
        user_role = None
        user_name = None
    else:
        is_authenticated = True
        is_guest = False
        user_role = request.session.get('user_role')
        user_name = request.session.get('user_name')

    employees = Emploees.objects.all().order_by('last_name', 'first_name')

    show_full_info = False
    can_add = False
    can_change = False
    can_delete = False
    
    if is_guest:
        show_full_info = False
        can_add = False
        can_change = False
        can_delete = False
    
    elif is_authenticated:
        show_full_info = True
        
        if user_role == 'director':
            can_add = True
            can_change = True
            can_delete = True
        elif user_role == 'deputy':
            can_add = False
            can_change = True
            can_delete = False
        elif user_role == 'secretary':
            can_add = False
            can_change = False
            can_delete = False

    context = {
        'title':'Список сотрудников',
        'employees': employees,
        'show_full_info': show_full_info,
        'can_add': can_add,
        'can_change': can_change,
        'can_delete': can_delete,
        'is_authenticated': is_authenticated,
        'is_guest': is_guest,
        'user_role': user_role,
        'user_name': user_name,
    }
    
    return render(request, 'dist/emploees.html', context)


def login_view(request: HttpRequest):
    if request.session.get('is_authenticated', False):
        messages.info(request, 'Вы уже вошли в систему')
        return redirect('index')
    
    if 'is_guest' in request.session:
        del request.session['is_guest']
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            
            request.session['is_authenticated'] = True
            request.session['user_id'] = user.id
            request.session['user_login'] = user.login
            request.session['user_role'] = user.employee.position
            request.session['user_name'] = user.employee.full_name
            
            messages.success(request, f'Добро пожаловать, {user.employee.full_name}!')
            return redirect('index')
    else:
        form = LoginForm()
    
    context = {
        'title':'Вход в систему',
        'form': form,
    }
    return render(request, 'dist/login.html', context)


def logout(request: HttpRequest):
    user_name = request.session.get('user_name', '')
    
    request.session.flush()
    
    if user_name:
        messages.success(request, f'До свидания, {user_name}!')
    else:
        messages.success(request, 'Вы вышли из системы')
    
    return redirect('index')


def employee_create(request: HttpRequest):
    if request.session.get('is_guest', False):
        messages.error(request, 'У вас нет прав для добавления сотрудников')
        return redirect('index')
    
    if not request.session.get('is_authenticated', False):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('login')
    
    user_role = request.session.get('user_role')
    if user_role != 'director':
        messages.error(request, 'Только директор может добавлять сотрудников')
        return redirect('index')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee, login, password = form.save()
            
            return render(request, 'dist/employee_created.html', {
                'title':'Создание работника',
                'employee': employee,
                'login': login,
                'password': password
            })
    else:
        form = EmployeeForm()
    
    context = {
        'title':'Создание работника',
        'form': form,
        'action': 'create'
    }
    return render(request, 'dist/employee_form.html', context)


def employee_update(request: HttpRequest, pk):
    """Редактирование сотрудника (директор и заместитель)"""
    if request.session.get('is_guest', False):
        messages.error(request, 'У вас нет прав для редактирования')
        return redirect('index')
    
    if not request.session.get('is_authenticated', False):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('login')
    
    user_role = request.session.get('user_role')
    if user_role not in ['director', 'deputy']:
        messages.error(request, 'У вас нет прав для редактирования')
        return redirect('index')
    
    employee = get_object_or_404(Emploees, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee, create_account=False)
        if form.is_valid():
            form.save()  
            messages.success(request, f'Данные сотрудника {employee.full_name} успешно обновлены')
            return redirect('index')
    else:
        form = EmployeeForm(instance=employee, create_account=False)
    
    context = {
        'title':'Обновление данных о работнике',
        'form': form,
        'action': 'update',
        'employee': employee,
    }
    return render(request, 'dist/employee_form.html', context)


def employee_delete(request: HttpRequest, pk):
    if request.session.get('is_guest', False):
        messages.error(request, 'У вас нет прав для удаления сотрудников')
        return redirect('index')
    
    if not request.session.get('is_authenticated', False):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('login')
    
    user_role = request.session.get('user_role')
    if user_role != 'director':
        messages.error(request, 'Только директор может удалять сотрудников')
        return redirect('index')
    
    employee = get_object_or_404(Emploees, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.full_name
        employee.delete()
        messages.success(request, f'Сотрудник {employee_name} успешно удален')
        return redirect('index')
    
    context = {
        'title':'Удалить работника из системы',
        'employee': employee,
    }
    return render(request, 'dist/employee_confirm_delete.html', context)