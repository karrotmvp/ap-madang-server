from rest_framework import viewsets, mixins, status
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from rest_framework.response import Response
from config.settings import API_KEY, BASE_URL_REGION
import json
import requests
from django.db.utils import IntegrityError


def send_biz_chat_message(
    user_id,
    title,
    text,
    primary_button_url,
    primary_button_text,
    is_normal_button,
    normal_button_url=None,
    normal_button_text=None,
):
    url = BASE_URL_REGION + "/api/v2/chat/send_biz_chat_message"

    actions = [
        {
            "payload": {
                "text": primary_button_text,
                "linkUrl": primary_button_url,
            },
            "type": "PRIMARY_BUTTON",
        }
    ]

    if is_normal_button:
        actions.append(
            {
                "payload": {"text": normal_button_text, "linkUrl": normal_button_url},
                "type": "NORMAL_BUTTON",
            }
        )

    payload = {
        "input": {
            "actions": actions,
            "userId": user_id,
            "title": title,
            "text": text,
        }
    }
    headers = {
        "Accept": "application/json",
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    request_data = json.loads(response.text).get("data", None)

    if request_data is None:
        print("***** Alarm talk sent failed!!! *****")
        print(response.text)
        return False

    return request_data.get("sendBizChatMessage", None).get("status", None) == "OK"


class UserMeetingAlarmViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserMeetingAlarmSerializer
    queryset = UserMeetingAlarm.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "이미 해당 유저가 해당 모임에 대한 알람을 신청한 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @jwt_authentication
    def destroy(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        if self.get_object().user.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "알람 신청한 유저만이 알람을 해제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
        )
