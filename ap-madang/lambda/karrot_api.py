import config
import json
import requests


def send_biz_chat_message(
    user_id,
    title,
    text,
    primary_button_url,
    primary_button_text,
    is_normal_button,
    normal_button_url=None,
    normal_button_text=None,
):
    url = config.dev_karrot_oapi_url + "/api/v2/chat/send_biz_chat_message"

    actions = [
        {
            "payload": {
                "text": primary_button_text,
                "linkUrl": primary_button_url,
            },
            "type": "PRIMARY_BUTTON",
        }
    ]

    if is_normal_button:
        actions.append(
            {
                "payload": {"text": normal_button_text, "linkUrl": normal_button_url},
                "type": "NORMAL_BUTTON",
            }
        )

    payload = {
        "input": {
            "actions": actions,
            "userId": user_id,
            "title": title,
            "text": text,
        }
    }
    headers = {
        "Accept": "application/json",
        "X-Api-Key": config.dev_api_key,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    request_data = json.loads(response.text).get("data", None)

    if request_data is None:
        print("***** Alarm talk sent failed!!! *****")
        print(response.text)
        return False

    return request_data.get("sendBizChatMessage", None).get("status", None) == "OK"
