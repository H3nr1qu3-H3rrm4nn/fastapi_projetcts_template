from os import getenv


def is_prod():
    return getenv("APP_PROFILE") == "prod"


def is_not_prod():
    return getenv("APP_PROFILE") != "prod"
