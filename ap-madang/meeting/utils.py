from datetime import date, timedelta

DAY_TO_MODEL = {
    0: "0_MON",
    1: "1_TUE",
    2: "2_WED",
    3: "3_THUR",
    4: "4_FRI",
    5: "5_SAT",
    6: "6_SUN",
}


def get_date_of_today():
    return DAY_TO_MODEL.get(date.today().weekday(), None)


def get_date_of_tomorrow():
    tommorow = date.today() + timedelta(days=1)
    return DAY_TO_MODEL.get(tommorow.weekday(), None)
