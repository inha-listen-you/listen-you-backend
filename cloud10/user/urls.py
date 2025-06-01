from django.urls import path
from .views import UserInfoView, SignupView

app_name = 'user'

urlpatterns = [
    # 유저 정보 조회
    path('info/', UserInfoView.as_view(), name='user-info'),
    path('signup/', SignupView.as_view(), name='signup'),
] 