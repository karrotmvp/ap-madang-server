from rest_framework.decorators import api_view
import json
from config.settings import JWT_SECRET
from oauth.views import (
    get_access_token_from_code,
    get_user_info,
    get_region_from_region_id,
    get_manner_temperature,
)
from django.http import HttpResponse, JsonResponse
from .models import User
from .serializers import UserSerializer
import jwt
from rest_framework import viewsets, mixins


@api_view(["POST"])
def login(request):
    code = json.loads(request.body)["code"]
    region_id = json.loads(request.body)["region_id"]
    # TODO body 값 없을 때 -> 404 Not Found

    # get access token
    access_token = get_access_token_from_code(code)
    if access_token is None:
        return HttpResponse(status=401)

    # get user info
    user_info = get_user_info(access_token)
    if user_info is None:
        return HttpResponse(status=401)

    karrot_user_id = user_info.get("user_id", None)
    nickname = user_info.get("nickname", None)
    profile_image_url = user_info.get("profile_image_url", None)
    manner_temperature = get_manner_temperature(karrot_user_id)

    # 지역(구) 정보 가져오기
    region_data = get_region_from_region_id(region_id)
    region_name = region_data.get("name")
    region_name2 = region_data.get("name2")
    # TODO region 문제 있을 때 에러 처리

    token = jwt.encode(
        {"nickname": nickname, "region": region_name2, "code": code},
        JWT_SECRET,
        algorithm="HS256",
    )

    User.objects.update_or_create(
        karrot_user_id=karrot_user_id,
        defaults={
            "nickname": nickname,
            "profile_image_url": profile_image_url,
            "manner_temperature": manner_temperature,
            "token": token,
            "region_name": region_name,
        },
    )
    return JsonResponse({"token": token}, status=200, safe=False)


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects

    def get_queryset(self):
        user_ids = [int(s) for s in self.request.query_params.get("ids").split(",")]
        return User.objects.filter(id__in=user_ids)
