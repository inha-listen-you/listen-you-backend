from django.urls import path
from .views import UserInfoView, UserConsultDateView

app_name = 'user'

urlpatterns = [
    # 유저 정보 조회
    path('info/', UserInfoView.as_view(), name='user-info'),
    # 상담 내역 날짜 조회
    path('date/', UserConsultDateView.as_view(), name='user-consult-date'),
] 