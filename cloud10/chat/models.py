from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid

# Create your models here.

class ConsultLog(models.Model):
    user_id = models.IntegerField(null=True)
    counsel_id = models.UUIDField(default=uuid.uuid4, editable=False)
    consel_history = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    report = models.JSONField(null=True)

    class Meta:
        db_table = 'consult_log'
