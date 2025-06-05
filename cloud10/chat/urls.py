from django.urls import path
from .views import RandomHashView

app_name = 'chat'

urlpatterns = [
    path('', RandomHashView.as_view(), name='random-hash'),
] 