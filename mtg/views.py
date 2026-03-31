from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from .models import SensorData
import json
from datetime import datetime
from .utils import Generator

generator = Generator(min_value=10, max_value=30, n1=5, n2=15)

def dashboard(request: HttpRequest):
    current_value = generator.generate_data()
    history = list(SensorData.objects.all()[:generator.n1 + 1])
    
    prev_value = history[1].value if len(history) >= 2 else None
    alert = generator.check_alert(current_value, prev_value)

    chart_data = SensorData.objects.all()[:20]
    chart_values = []
    chart_timestamps = []
    chart_colors = []

    color_map = {
        'normal': 'rgb(75, 192, 192)',      
        'warning': 'rgb(255, 159, 64)',     
        'danger': 'rgb(255, 99, 132)',      
    }

    for data in reversed(chart_data):
        chart_values.append(data.value)
        chart_timestamps.append(data.timestamp.strftime("%H:%M:%S"))
        chart_colors.append(color_map.get(data.alert_type, color_map['normal']))
    
    filtered_data = request.session.get('filtered_data', None)
    last_filter = request.session.get('last_filter', None)
    
    context = {
        'current_value': round(current_value,0),
        'history': history,
        'n1': generator.n1,
        'alert': alert,
        'n2': generator.n2,
        'timestamp': datetime.now().timestamp(),
        'chart_values': json.dumps(chart_values),
        'chart_timestamps': json.dumps(chart_timestamps),
        'chart_colors': json.dumps(chart_colors),
        'total_count': SensorData.objects.count(),
        'min_value': generator.min_value,
        'max_value': generator.max_value,
        'filtered_data': json.dumps(filtered_data) if filtered_data else 'null',
        'last_filter': last_filter,
    }
    return render(request, 'mtg/dashboard.html', context)

def filter_data(request: HttpRequest):
    if request.method == 'GET':
        filter_type = request.GET.get('filter_type')
        filter_value = request.GET.get('filter_value')

        if not filter_value:
            return JsonResponse({'error': 'Значение должно быть числом'}, status=400)
        
        try:
            filter_value = float(filter_value)
        except ValueError:
            return JsonResponse({'error': 'Значение должно быть числом'}, status=400)
        
        
        all_data = SensorData.objects.all()[:100]

        filtered_data = []
        for data in all_data:
            if filter_type == 'greater' and data.value > filter_value:
                filtered_data.append(data)
            elif filter_type == 'less' and data.value < filter_value:
                filtered_data.append(data)
            elif filter_type == 'multiple' and abs(data.value % filter_value) < 1e-9:
                filtered_data.append(data)
        
        if filtered_data:
            filtered_data_sorted = sorted(filtered_data, key=lambda x: x.timestamp)
            values = [d.value for d in filtered_data_sorted]  
            timestamps = [d.timestamp.strftime("%H:%M:%S") for d in filtered_data_sorted]
            average = sum(values) / len(values) if values else 0

            bar_data = []
            for i, data in enumerate(filtered_data_sorted):
                bar_data.append({
                    'index': i + 1,
                    'value': data.value,
                    'timestamp': data.timestamp.strftime("%H:%M:%S")
                })
            
            result_data = {
                'values': values,
                'timestamps': timestamps,
                'average': round(average, 0),
                'count': len(filtered_data),
                'bar_data': bar_data,
                'filter_type': filter_type,
                'filter_value': filter_value,
            }
            
            request.session['filtered_data'] = result_data
            request.session['last_filter'] = {
                'type': filter_type,
                'value': filter_value
            }
            
            return JsonResponse({
                'status': 'success',
                'data': result_data
            })
        else:
            request.session.pop('filtered_data', None)
            request.session.pop('last_filter', None)
            
            return JsonResponse({
                'status': 'empty',
                'message': f'Нет данных, удовлетворяющих условию'
            })

def clear_filter(request):
    if request.method == 'POST':
        request.session.pop('filtered_data', None)
        request.session.pop('last_filter', None)
        return JsonResponse({'status': 'success', 'message': 'Фильтр очищен'})
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)

def data_clear(request):
    if request.method == 'POST':
        count = SensorData.objects.count()
        SensorData.objects.all().delete()
        
        request.session.pop('filtered_data', None)
        request.session.pop('last_filter', None)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Удалено {count} записей',
                'count': count
            })
    
    return redirect('dashboard')