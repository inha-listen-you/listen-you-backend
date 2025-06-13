from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import uuid

# 유저 모델 (users 테이블)
class User(models.Model):
    username = models.CharField(max_length=50, null=False)
    password = models.CharField(max_length=50, null=True)
    consult_list = ArrayField(
        models.UUIDField(),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'users'  # 테이블 이름을 'users'로 수정