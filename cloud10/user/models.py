from django.db import models
from django.utils import timezone

# 유저 모델 (users 테이블)
class User(models.Model):
    username = models.CharField(max_length=50, null=False)
    email = models.CharField(max_length=254, null=True)
    password = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(null=False)
    
    class Meta:
        db_table = 'users'  # 테이블 이름을 'users'로 수정
