from django.db import models
from django.contrib.auth.hashers import make_password,check_password

# Create your models here.

class Emploees(models.Model):
    ROLE_CHOICES = [
        ('director', 'Директор'),
        ('deputy', 'Заместитель директора'),
        ('secretary', 'Секретарь'),
    ]
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    patronymic = models.CharField('Отчество', max_length=100, blank=True)
    position = models.CharField('Должность',choices=ROLE_CHOICES,max_length=100)
    address = models.CharField('Адрес', max_length=300)
    phone = models.CharField('Телефон', max_length=20)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

class Logins(models.Model):
    employee = models.OneToOneField(
        Emploees,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник',
        related_name='account'
    )
    login = models.CharField('Логин', max_length=100, unique=True) 
    password = models.CharField('Пароль', max_length=255)
    

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)