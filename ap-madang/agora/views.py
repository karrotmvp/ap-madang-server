from .models import MeetingEnterCode
from .serializers import MeetingEnterCodeSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
from user.jwt_authentication import jwt_authentication_fbv
from meeting.models import MeetingLog
import requests
import json
from config.settings import AGORA_CUSTOMER_ID, AGORA_APP_ID
from .utils import *


@api_view(["GET"])
def get_user_meeting_from_code(request):
    code = request.GET.get("code", None)
    try:
        meeting_enter_code = MeetingEnterCode.objects.get(
            code=code, is_valid=True)
    except MeetingEnterCode.DoesNotExist:
        return JsonResponse({"error_code": "INVALID_CODE"}, status=401)

    meeting_enter_code.is_valid = False
    meeting_enter_code.save()
    serializer = MeetingEnterCodeSerializer(meeting_enter_code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@jwt_authentication_fbv
def get_meeting_enter_code(request):
    meeting_id = request.GET.get("meeting", None)
    # TODO 쿼리 파라미터 없는 경우
    code = MeetingEnterCode.objects.create(
        meeting=MeetingLog.objects.get(id=meeting_id), user=request.user
    )
    return JsonResponse({"code": code.code}, status=201, safe=False)


def get_agora_channel_user_list(channel_name):
    url = "https://api.agora.io/dev/v1/channel/user/{}/{}".format(
        AGORA_APP_ID, channel_name)

    payload = {}
    headers = {
        'Authorization': 'Basic ' + str(get_agora_credentials())
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


def is_agora_channel_available(channel_name):
    response_data = get_agora_channel_user_list(channel_name).get("data")

    channel_exist = response_data.get("channel_exist")
    if not channel_exist:
        return True
    total = response_data.get("total")
    return total < 17
