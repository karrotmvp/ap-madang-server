from rest_framework.decorators import api_view
from config.settings import CLIENT_BASE_URL
from .models import *
from .utils import *

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

    url = create_meeting_short_url(origin_url, meeting_id)
    return JsonResponse({"short_url": url}, status=200, safe=False)


def redirect_to_karrot_scheme(request):
    code = request.GET.get("share_code", None)
    short_url = get_object_or_404(ShareUrl, code=code)
    short_url.access_cnt += 1
    short_url.save()
    return redirect(short_url.karrot_scheme_url)


def get_karrot_scheme_url(request):
    code = request.GET.get("share_code", None)
    short_url = get_object_or_404(ShareUrl, code=code)
    short_url.access_cnt += 1
    short_url.save()
    return JsonResponse(
        {"karrot_scheme_url": short_url.karrot_scheme_url}, status=200, safe=False
    )
