// dashboard.js
let chart = null;
let filteredChart = null;
let barChart = null;

// Функция для создания или обновления графика
function updateChart(values, timestamps, colors) {
    const ctx = document.getElementById('sensorChart').getContext('2d');
    
    const datasets = [{
        label: 'Значение датчика',
        data: values,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: colors,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        tension: 0.1,
        fill: true
    }];
    
    if (chart) {
        chart.data.datasets = datasets;
        chart.data.labels = timestamps;
        chart.update();
    } else {
        chart = new Chart(ctx, {
            type: 'line',
            data: { labels: timestamps, datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                label += context.raw.toFixed(2);
                                const colors = context.dataset.pointBackgroundColor;
                                if (Array.isArray(colors) && colors[context.dataIndex]) {
                                    if (colors[context.dataIndex].includes('255, 99, 132')) {
                                        label += 'ТРЕВОГА!';
                                    } else if (colors[context.dataIndex].includes('255, 159, 64')) {
                                        label += 'Предупреждение!';
                                    }
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: false, title: { display: true, text: 'Значение' } },
                    x: { title: { display: true, text: 'Время' }, ticks: { maxRotation: 45, minRotation: 45 } }
                }
            }
        });
    }
}

// Функция для обновления графика выборочных данных
function updateFilteredChart(values, timestamps, average) {
    const ctx = document.getElementById('filteredChart').getContext('2d');
    
    const datasets = [{
        label: 'Выборочные значения',
        data: values,
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        borderWidth: 2,
        pointRadius: 6,
        pointBackgroundColor: 'rgb(54, 162, 235)',
        tension: 0.1,
        fill: true
    }];
    
    // Добавляем линию среднего значения
    if (average > 0) {
        datasets.push({
            label: `Среднее значение: ${average}`,
            data: Array(values.length).fill(average),
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0)',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
        });
        
        // Обновляем информацию о среднем
        const avgInfo = document.getElementById('averageInfo');
        if (avgInfo) {
            avgInfo.innerHTML = `Среднее значение выборочных данных: <strong>${average}</strong>`;
        }
    }
    
    if (filteredChart) {
        filteredChart.data.datasets = datasets;
        filteredChart.data.labels = timestamps;
        filteredChart.update();
    } else {
        filteredChart = new Chart(ctx, {
            type: 'line',
            data: { labels: timestamps, datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: { title: { display: true, text: 'Значение' } },
                    x: { title: { display: true, text: 'Время' } }
                }
            }
        });
    }
}

// Функция для обновления столбчатой диаграммы
function updateBarChart(barData) {
    const ctx = document.getElementById('barChart').getContext('2d');
    
    const labels = barData.map(item => item.timestamp);
    const values = barData.map(item => item.value);
    
    if (barChart) {
        barChart.data.labels = labels;
        barChart.data.datasets[0].data = values;
        barChart.update();
    } else {
        barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Значения',
                    data: values,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgb(75, 192, 192)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { 
                        callbacks: {
                            label: function(context) {
                                return `Значение: ${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: { 
                        title: { display: true, text: 'Значение' },
                        beginAtZero: true
                    },
                    x: { 
                        title: { display: true, text: 'Время' },
                        ticks: { maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });
    }
}

// Функция для применения фильтра
async function applyFilter() {
    const filterType = document.getElementById('filterType').value;
    const filterValue = document.getElementById('filterValue').value;
    
    if (!filterValue) {
        showNotification('Введите значение для фильтрации', 'warning');
        return;
    }

    
    
    const url = `${filterUrl}?filter_type=${filterType}&filter_value=${filterValue}`;
    
    try {
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.status === 'success') {
            const data = result.data;
            
            // Показываем секцию с выборочными данными
            document.getElementById('filteredDataSection').style.display = 'block';
            
            // Обновляем информацию о фильтре
            const filterInfo = document.getElementById('filterInfo');
            filterInfo.innerHTML = `
                <strong>Фильтр: ${getFilterTypeName(filterType)} ${filterValue}</strong><br>
                Найдено записей: ${data.count}<br>
                Среднее значение: ${data.average}
            `;
            filterInfo.style.display = 'block';
            
            // Обновляем графики
            updateFilteredChart(data.values, data.timestamps, data.average);
            updateBarChart(data.bar_data);
            
            showNotification(`Найдено ${data.count} записей`, 'success');
        } else if (result.status === 'empty') {
            document.getElementById('filteredDataSection').style.display = 'none';
            document.getElementById('filterInfo').innerHTML = `
                <strong>${result.message}</strong>
            `;
            filterInfo.style.display = 'block';
            showNotification(result.message, 'warning');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при фильтрации данных', 'error');
    }
}

// Функция сброса фильтра
async function resetFilter() {
    try {
        // Отправляем запрос на очистку фильтра на сервере
        const response = await fetch(clearFilterUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            document.getElementById('filterType').value = 'greater';
            document.getElementById('filterValue').value = '';
            document.getElementById('filteredDataSection').style.display = 'none';
            document.getElementById('filterInfo').style.display = 'none';
            document.getElementById('filterInfo').innerHTML = '';
            
            // Очищаем графики
            if (filteredChart) {
                filteredChart.destroy();
                filteredChart = null;
            }
            if (barChart) {
                barChart.destroy();
                barChart = null;
            }
            
            showNotification('Фильтр очищен', 'success');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка при очистке фильтра', 'error');
    }
}

// Вспомогательная функция для получения названия типа фильтра
function getFilterTypeName(type) {
    const types = {
        'greater': 'больше',
        'less': 'меньше',
        'multiple': 'кратно'
    };
    return types[type] || type;
}

// Функция для восстановления сохраненного фильтра
function restoreSavedFilter() {
    const savedDataElement = document.getElementById('saved-filter-data');
    if (savedDataElement && savedDataElement.dataset.filteredData) {
        try {
            const filteredData = JSON.parse(savedDataElement.dataset.filteredData);
            if (filteredData && filteredData.values && filteredData.values.length > 0) {
                // Показываем секцию
                document.getElementById('filteredDataSection').style.display = 'block';
                
                // Обновляем информацию
                const filterInfo = document.getElementById('filterInfo');
                filterInfo.innerHTML = `
                    <strong>Фильтр: ${getFilterTypeName(filteredData.filter_type)} ${filteredData.filter_value}</strong><br>
                    Найдено записей: ${filteredData.count}<br>
                    Среднее значение: ${filteredData.average}
                `;
                filterInfo.style.display = 'block';
                
                // Восстанавливаем графики
                updateFilteredChart(filteredData.values, filteredData.timestamps, filteredData.average);
                updateBarChart(filteredData.bar_data);
            }
        } catch (e) {
            console.error('Ошибка восстановления фильтра:', e);
        }
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

async function clearData() {
    if (!confirm('Вы уверены, что хотите очистить все данные? Это действие нельзя отменить.')) {
        return;
    }
    try{
        const response = await fetch(clearUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();
            showNotification(data.message, 'success');
            
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification('Ошибка при очистке данных', 'error');
        }
    } catch(e) {
        console.error('Ошибка:', e);
        showNotification('Ошибка соединения', 'error');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация основного графика
    const container = document.getElementById('chart-data');
    if (container) {
        try {
            const values = JSON.parse(container.dataset.chartValues);
            const timestamps = JSON.parse(container.dataset.chartTimestamps);
            const colors = JSON.parse(container.dataset.chartColors);
            
            if (values && timestamps && colors) {
                updateChart(values, timestamps, colors);
            }
        } catch (e) {
            console.error('Ошибка парсинга данных графика:', e);
        }
    }
    
    // Восстанавливаем сохраненный фильтр
    restoreSavedFilter();
    
    // Назначаем обработчики для фильтров
    const applyBtn = document.getElementById('applyFilterBtn');
    const resetBtn = document.getElementById('resetFilterBtn');
    const clearBtn = document.getElementById('clearDataBtn');
    
    if (applyBtn) {
        applyBtn.addEventListener('click', applyFilter);
    }
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilter);
    }
    if (clearBtn) {
        clearBtn.addEventListener('click', clearData);
    }
    
    // Автообновление страницы
    setTimeout(function() {
        location.reload();
    }, 10000);
});