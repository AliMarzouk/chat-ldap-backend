from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from rest_framework import routers

from rest_framework.routers import DefaultRouter
from chat.views import *
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.SimpleRouter()
router.register(r'users', UserView)

urlpatterns = [
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('token/', CustomTokenPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('snippets/', SnippetList.as_view()),
    path('users/create', UserView.as_view()),
    # router.urls,
]
