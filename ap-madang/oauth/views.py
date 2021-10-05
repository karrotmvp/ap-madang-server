from django.shortcuts import render
import requests
from config.settings import APP_ID_SECRET, API_KEY

BASE_URL = "https://openapi.kr.karrotmarket.com"

# Create your views here.


def get_access_token_from_code(code):
    url = BASE_URL + "/oauth/token"

    querystring = {
        "code" : code,
        "grant_type" : "authorization_code",
        "scope" : "account/profile",
        "response_type" : "code"
    }

    headers = {"Authorization": "Basic " + APP_ID_SECRET }
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return response.text.get("access_token", None)

def get_user_info(access_token):
    url = BASE_URL + "/api/v1/users/me"

    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token
    }

    response = requests.request("GET", url, headers=headers)
    return response.text

def get_region_from_region_id(region_id):
    url = BASE_URL + "/api/v2/region/" + region_id

    headers = {
        "X-Api-Key": API_KEY
    }
    response = requests.request("GET", url, headers=headers)
    return response.text


    