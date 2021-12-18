from config.settings import ENV_NAME


def get_env_name():
    # returns dev / prod / other
    if ENV_NAME in ["dev", "dev-sub"]:
        return "dev"
    if ENV_NAME in ["production", "production-sub"]:
        return "prod"
    return "other"
