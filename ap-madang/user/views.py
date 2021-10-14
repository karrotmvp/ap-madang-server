from rest_framework.decorators import api_view
import json
from config.settings import JWT_SECRET
from oauth.views import (
    get_access_token_from_code,
    get_user_info,
    get_region_from_region_id,
    get_manner_point,
)
from django.http import HttpResponse, JsonResponse
from .models import User
import jwt


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
    manner_point = get_manner_point(access_token)
    if (user_info is None) or (manner_point is None):
        return HttpResponse(status=401)

    karrot_user_id = user_info.get("user_id", None)
    nickname = user_info.get("nickname", None)
    profile_image_url = user_info.get("profile_image_url", None)

    # 지역(구) 정보 가져오기
    region = get_region_from_region_id(region_id).get("name2")
    # TODO region 문제 있을 때 에러 처리

    user, is_created = User.objects.update_or_create(
        karrot_user_id=karrot_user_id,
        defaults={
            "nickname": nickname,
            "profile_image_url": profile_image_url,
            "manner_point": manner_point,
        },
    )

    print(is_created, karrot_user_id, nickname, profile_image_url, manner_point, region)

    token = jwt.encode({"id": user.id, "region": region}, JWT_SECRET, algorithm="HS256")

    return JsonResponse(
        {"token": token, "nickname": nickname, "region": region}, status=200, safe=False
    )
