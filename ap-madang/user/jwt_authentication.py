import jwt
from .models import User
from django.http import JsonResponse
from config.settings import JWT_SECRET


def jwt_authentication(func):
    def wrapper(self, request, *args, **kwargs):

        # 프론트에서 헤더에 토큰 제공하지 않았을 경우 -> 401 Unauthorized
        if "Authorization" not in request.headers:
            return JsonResponse({"error_code": "JWT_MISSING"}, status=401)

        encode_token = request.headers["Authorization"]
        try:
            data = jwt.decode(encode_token, JWT_SECRET, algorithms="HS256")
            user = User.objects.get(id=data["id"])
            request.region = data["region"]
            request.user = user

        # 잘못된 토큰 ( 서버에서 발행한 토큰이 아님)
        except jwt.DecodeError:
            return JsonResponse({"error_code": "INVALID_TOKEN"}, status=401)

        # 유저의 정보가 없음(유효하지 않은 토큰)
        except User.DoesNotExist:
            return JsonResponse({"error_code": "UNKNOWN_USER"}, status=401)

        return func(self, request, *args, **kwargs)

    return wrapper
