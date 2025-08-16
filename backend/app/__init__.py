from app.views.routes import BB_BASE_URL, BB_CLIENT_ID, BB_CLIENT_SECRET, BB_REDIRECT_URI, WEB_ORIGIN
from flask import Flask
from app.src.token_manager import TokenManager

def create_app() -> Flask:
    app = Flask(__name__)
    from .views.routes import api, SECRET_KEY
    app.register_blueprint(api)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["BB_BASE_URL"] = BB_BASE_URL
    app.config["BB_CLIENT_ID"] = BB_CLIENT_ID
    app.config["BB_CLIENT_SECRET"] = BB_CLIENT_SECRET
    app.config["BB_REDIRECT_URI"] = BB_REDIRECT_URI
    app.config["WEB_ORIGIN"] = WEB_ORIGIN
    app.extensions["bb_tokens"] = TokenManager(
        base_url=app.config["BB_BASE_URL"],
        client_id=app.config["BB_CLIENT_ID"],
        client_secret=app.config["BB_CLIENT_SECRET"],
    )
    return app



if __name__ == "__main__":
    app = create_app()
    