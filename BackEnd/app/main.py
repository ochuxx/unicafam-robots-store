from flask import Flask
from dotenv import load_dotenv

from .config import get_config
from .routes import api


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.update(get_config())
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/")
    def index():
        return {"status": "ok", "service": "unicafam-robots-store"}

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
