DEFAULT_PROFILE_IMAGE_URL = {
    0: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default1.png",
    1: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default2.png",
    2: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default3.png",
    3: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default4.png",
}


def get_profile_image_url(user):
    return (
        user.profile_image_url
        if user.profile_image_url
        else DEFAULT_PROFILE_IMAGE_URL.get(user.id % 4)
    )
