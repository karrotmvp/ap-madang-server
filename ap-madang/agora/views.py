from .models import MeetingEnterCode
from .serializers import MeetingEnterCodeSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["GET"])
def get_user_meeting_from_code(request):
    code = request.GET.get("code", None)
    try:
        meeting_enter_code = MeetingEnterCode.objects.get(code=code, is_valid=True)
    except MeetingEnterCode.DoesNotExist:
        return JsonResponse({"error_code": "INVALID_CODE"}, status=401)

    meeting_enter_code.is_valid = False
    meeting_enter_code.save()
    serializer = MeetingEnterCodeSerializer(meeting_enter_code)
    return Response(serializer.data, status=status.HTTP_200_OK)
