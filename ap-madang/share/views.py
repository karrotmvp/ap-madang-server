from rest_framework.decorators import api_view
from config.settings import CLIENT_BASE_URL, SERVER_SHORT_URL_BASE_URL
from .models import *
from .utils import *
from oauth.views import get_karrot_scheme
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect

HttpResponseRedirect.allowed_schemes.append("karrot")
HttpResponseRedirect.allowed_schemes.append("karrot.alpha")

# Create your views here.
@api_view(["GET"])
def get_or_create_short_url(request):
    meeting_id = request.GET.get("meeting", None)
    origin_url = "{}/index.html?#/meetings/{}?ref=share".format(
        CLIENT_BASE_URL, meeting_id
    )

    short_url, created = ShareUrl.objects.get_or_create(
        origin_url=origin_url,
        defaults={
            "karrot_scheme_url": get_karrot_scheme(origin_url),
            "code": create_url_code(origin_url, meeting_id),
        },
    )

    url = "{}/share/redirect?code={}".format(SERVER_SHORT_URL_BASE_URL, short_url.code)

    return JsonResponse({"short_url": url}, status=200, safe=False)


def redirect_to_karrot_scheme(request):
    code = request.GET.get("code", None)
    short_url = get_object_or_404(ShareUrl, code=code)
    short_url.access_cnt += 1
    short_url.save()
    return redirect(short_url.karrot_scheme_url)
