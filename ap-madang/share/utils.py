import hashlib


def create_url_code(origin_url, meeting_id):
    return hashlib.md5(origin_url.encode()).hexdigest()[:5] + meeting_id
