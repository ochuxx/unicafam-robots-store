import os


def get_config() -> dict:
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev-only"),
        "GAS_URL": os.getenv("GAS_URL", ""),
    }
