from django.shortcuts import render
import requests
from config.settings import APP_ID_SECRET, API_KEY, BASE_URL_REGION, BASE_URL_OAUTH
import json


def get_access_token_from_code(code):
    url = BASE_URL_OAUTH + "/oauth/token"

    querystring = {
        "code": code,
        "grant_type": "authorization_code",
        "scope": "account/profile",
        "response_type": "code",
    }

    headers = {"Authorization": "Basic " + APP_ID_SECRET}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return json.loads(response.text).get("access_token", None)


def get_user_info(access_token):
    url = BASE_URL_OAUTH + "/api/v1/users/me"

    headers = {"Accept": "application/json", "Authorization": "Bearer " + access_token}

    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text).get("data", None)


def get_region_from_region_id(region_id):
    # name depth를 지정해서 사용해야됨
    url = BASE_URL_REGION + "/api/v2/regions/" + str(region_id)

    headers = {"X-Api-Key": API_KEY}
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text).get("data").get("region")


def get_manner_point(access_token):
    url = BASE_URL_OAUTH + "/api/v1/users/me/manner_point"

    headers = {"Accept": "application/json", "Authorization": "Bearer " + access_token}

    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text).get("data").get("manner_point")
