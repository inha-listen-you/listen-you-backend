from django.urls import path
from .views import UserInfoView

app_name = 'user'

urlpatterns = [
    path('info/', UserInfoView.as_view(), name='user_info'),
] 