from django.db import models

# Create your models here.
class SensorData(models.Model):
    ALERT_CHOICES = [
        ('normal', 'Норма'),
        ('warning', 'Предупреждение'),
        ('danger', 'Тревога'),
    ]

    value = models.FloatField()
    timestamp=models.DateTimeField(auto_now_add=True)
    alert_type=models.CharField(
        max_length=10,
        choices=ALERT_CHOICES,
        default='normal'
    )

    class Meta:
        ordering=['-timestamp']


    def __str__(self):
        return f"{self.value}"