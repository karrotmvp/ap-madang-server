from oauth.views import get_access_token_from_code, get_user_info, get_region_from_region_id
import json
from django.http import HttpResponse, JsonResponse
from .models import Reservation
from rest_framework.decorators import api_view

@api_view(['POST'])
def reservation(request):
    '''
    사전 예약 등록 API
    ---
    사전 예약을 신청한 유저의 정보를 등록합니다
    '''

    # body
    code = json.loads(request.body)['code']
    region_id = json.loads(request.body)['region_id']
    suggestion = json.loads(request.body)['suggestion']

    # get user info
    access_token = get_access_token_from_code(code)
    if access_token is None:
        return HttpResponse(status=401)
    # code가 만료된 경우 -> 예외처리 
    
    user_info = get_user_info(access_token)
    if user_info is None:
        return HttpResponse(status=401)

    user_id = user_info.get("user_id", None)
    nickname = user_info.get("nickname", None)
    region = get_region_from_region_id(region_id).get("name")
    
    # save reservation data
    reservation = Reservation.objects.create( 
            userid = user_id, nickname = nickname, region = region, suggestion = suggestion)

    return HttpResponse(status=201)

@api_view(['GET'])
def region(request):
    '''
    지역(구) 정보 조회 API
    ---
    region_id를 기준으로 지역구를 조회합니다
    '''
    region_id = request.GET.get("region_id", None)
    region_name = get_region_from_region_id(region_id).get("name2")

    return JsonResponse({'region': region_name},status=200, safe=False)