"""ap-madang URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .settings import ENV_NAME


def env_name(request):
    return HttpResponse("This is daangn-meetup " + ENV_NAME)


schema_view = get_schema_view(
    openapi.Info(
        title="Online Town Meeting API",
        default_version="v1",
        description="랜던 동네 모임 API 문서",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", env_name),
    path("admin/", admin.site.urls),
    path("oauth/", include("oauth.urls")),
    path("reservation/", include("reservation.urls")),
    path("users/", include("user.urls")),
    path("meetings/", include("meeting.urls")),
    path("alarms/", include("alarmtalk.urls")),
    path("support/", include("support.urls")),
]


urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
