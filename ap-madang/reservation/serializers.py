from rest_framework import serializers

class ReservationBodySerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Oauth 인가 코드")
    region_id = serializers.CharField(help_text="지역 아이디")
    suggestion = serializers.CharField(allow_blank=True, allow_null=True, help_text="유저 주관식 답안")