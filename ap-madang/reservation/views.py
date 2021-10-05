from django.shortcuts import render
from oauth import views
from django.http import HttpResponse

# Create your views here.

def reservation(request):
    # body
    code = json.loads(request.body)['code']
    region_id = json.loads(request.body)['region_id']

    # get user info
    access_token = get_access_token_from_code(code)
    user_info = get_user_info(access_token)

    user_id = user_info.get("user_id", None)
    nickname = user_info.get("nickname", None)
    region = get_region_from_region_id(region_id)

    # save reservation data
    reservation = Reservation.objects.create( 
            userid = user_id, nickname = nickname, region = region)

    
    return HttpResponse(status=201)






