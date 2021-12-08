def date_and_time_to_korean(date, time):

    return "{}년 {}월 {}일 {}시 {}분".format(
        date.strftime("%Y"),
        date.strftime("%-m"),
        date.strftime("%-d"),
        time.strftime("%-H"),
        time.strftime("%-M"),
    )
