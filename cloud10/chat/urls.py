from django.urls import path
from .views import RandomHashView, GenerateAIMessageView, SummarizeConsultLogView, WeeklyConsultCountView

app_name = 'chat'

urlpatterns = [
    path('', RandomHashView.as_view(), name='random-hash'),
    path('generate/', GenerateAIMessageView.as_view(), name='generate-ai-message'),
    path('end/', SummarizeConsultLogView.as_view(), name='summarize-consultlog'),
    path('weeklycount/', WeeklyConsultCountView.as_view(), name='weekly-consult-count'),
]