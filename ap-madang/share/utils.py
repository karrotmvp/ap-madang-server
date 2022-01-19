import hashlib
from .models import *
from oauth.views import get_karrot_scheme
from config.settings import SERVER_SHORT_URL_BASE_URL


def create_url_code(origin_url, meeting_id):
    return hashlib.md5(origin_url.encode()).hexdigest()[:5] + meeting_id


def create_meeting_short_url(origin_url, meeting_id):
    short_url, created = ShareUrl.objects.get_or_create(
        origin_url=origin_url,
        defaults={
            "karrot_scheme_url": get_karrot_scheme(origin_url),
            "code": create_url_code(origin_url, str(meeting_id)),
        },
    )

    url = "{}/share/redirect?code={}".format(SERVER_SHORT_URL_BASE_URL, short_url.code)

    return url
