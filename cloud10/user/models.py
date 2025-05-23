from django.db import models

# 유저 모델 (user 테이블)
class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'user'  
