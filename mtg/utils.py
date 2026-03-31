import random 
from .models import SensorData

class Generator:
    def __init__(self,min_value=10,max_value=30,n1=5,n2=15):
        self.min_value=min_value
        self.max_value=max_value
        self.n1=n1
        self.n2=n2

    def generate_data(self):
        new_value=round(random.uniform(self.min_value-5,self.max_value+5),0)
        last_record=SensorData.objects.first()
        prev_value=last_record.value if last_record else None

        alert_type =self._determinate_alert_type(new_value,prev_value)
        SensorData.objects.create(value=new_value,alert_type=alert_type)
        return new_value
    
    def _determinate_alert_type(self,current_value,prev_value=None):
        if current_value < self.min_value or current_value > self.max_value:
            return 'danger'
        
        if prev_value is not None:
            change_percent = abs((current_value - prev_value) / prev_value * 100)
            if change_percent > self.n2:
                return 'warning'
        
        return 'normal'

    def set_range(self, min_val, max_val):
        self.min_value = min_val
        self.max_value = max_val
    
    def set_alert_threshold(self, n2):
        self.n2 = n2
    
    def check_alert(self,current_value,prev_value=None):
        if current_value<self.min_value or current_value>self.max_value:
            return{
                'type': 'danger',
                'message': f'Danger!!! Значение {current_value:.1f} вне диапазона [{self.min_value}, {self.max_value}]'
            }
        if prev_value is not None:
            change_percent = abs((current_value - prev_value) / prev_value * 100)
            if change_percent > self.n2:
                return {
                    'type': 'warning',
                    'message': f'Warning!!! Изменение на {change_percent:.1f}% (превышает {self.n2}%)'
                }
        return None
        