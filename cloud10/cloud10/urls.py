from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),  # user 앱의 URL 패턴 포함
    path('login/', include('login.urls')),
    path('chat/', include('chat.urls')),
]
