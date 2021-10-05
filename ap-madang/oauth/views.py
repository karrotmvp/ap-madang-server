from django.shortcuts import render
import requests

# Create your views here.

def me(request):
    # code 받아오기
    code = request.GET.get("code", None)
    
    # auth token 받아오기
    
    url = "https://openapi.kr.karrotmarket.com/oauth/token"

    querystring = {
        "code" : code,
        "grant_type" : "authorization_code",
        "scope" : "account/profile",
        "response_type" : "code"
    }
    headers = {"Authorization": "Basic " + "appId:appSecret" }
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)


    # token 으로 유저 정보 받아오기