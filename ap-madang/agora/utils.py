import http.client
import base64
from config.settings import AGORA_CUSTOMER_ID, AGORA_CUSTOMER_SECRET


def get_agora_credentials():

    # -- coding utf-8 --
    # Python 3
    # HTTP basic authentication example in python using the RTC Server RESTful API

    # Customer ID
    customer_key = AGORA_CUSTOMER_ID
    # Customer secret
    customer_secret = AGORA_CUSTOMER_SECRET

    # Concatenate customer key and customer secret and use base64 to encode the concatenated string
    credentials = customer_key + ":" + customer_secret
    # Encode with base64
    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")
    return credential
