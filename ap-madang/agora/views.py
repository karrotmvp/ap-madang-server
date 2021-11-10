import random
import string
import datetime

# from AgoraDynamicKey.RtcTokenBuilder import *
# from config.settings import AGORA_APP_ID, AGORA_APP_CERTIFICATE


# Create your views here.
def create_channel_name():
    return (
        str(datetime.datetime.now())
        + "_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=20))
    )


# def create_agora_token(meeting, user):
#     return RtcTokenBuilder.buildTokenWithUid(
#         AGORA_APP_ID,
#         AGORA_APP_CERTIFICATE,
#         meeting.channel_name,
#         user.id,
#         Role_Attendee,
#         0,
#     )
