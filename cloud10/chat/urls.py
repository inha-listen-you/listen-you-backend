from django.urls import path
from .views import RandomHashView, GenerateAIMessageView

app_name = 'chat'

urlpatterns = [
    path('', RandomHashView.as_view(), name='random-hash'),
    path('generate/', GenerateAIMessageView.as_view(), name='generate-ai-message'),
    
]