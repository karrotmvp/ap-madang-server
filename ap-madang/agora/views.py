import random
import string
import datetime

# Create your views here.
def create_channel_name():
    return (
        str(datetime.datetime.now())
        + "_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=20))
    )
