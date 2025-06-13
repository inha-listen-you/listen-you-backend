from django.urls import path
from .views import RandomHashView, GenerateAIMessageView
from .views import ConsultLogListView
app_name = 'chat'

urlpatterns = [
    path('', RandomHashView.as_view(), name='random-hash'),
    path('generate/', GenerateAIMessageView.as_view(), name='generate-ai-message'),
    path('info/', ConsultLogListView.as_view(), name='consult-log-list'),
]