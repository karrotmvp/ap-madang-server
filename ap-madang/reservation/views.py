from django.shortcuts import render
from oauth.views import get_access_token_from_code, get_user_info, get_region_from_region_id
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from .models import Reservation
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import ReservationBodySerializer
# Create your views here.

BASE_URL = "https://openapi.alpha.kr.karrotmarket.com"

# Create your views here.

@api_view(['POST'])
@swagger_auto_schema(request_body=ReservationBodySerializer)
def reservation(request):
    # body
    code = json.loads(request.body)['code']
    region_id = json.loads(request.body)['region_id']
    suggestion = json.loads(request.body)['suggestion']

    # get user info
    access_token = get_access_token_from_code(code).get("access_token", None)
    if access_token is None:
        return HttpResponse(status=401)
    # code가 만료된 경우 -> 예외처리 
    
    user_info = get_user_info(access_token).get("data", None)
    if user_info is None:
        return HttpResponse(status=401)

    user_id = user_info.get("user_id", None)
    nickname = user_info.get("nickname", None)
    region = get_region_from_region_id(region_id).get("data").get("region").get("name")
    print(user_id, nickname, region)
    
    # save reservation data
    reservation = Reservation.objects.create( 
            userid = user_id, nickname = nickname, region = region, suggestion = suggestion)

    return HttpResponse(status=201)






