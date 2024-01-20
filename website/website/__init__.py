from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from secrets import token_bytes


# Generate database.db tables from generate_database.sql
DB_NAME = "database.db"
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    db = SQLAlchemy()

    app.config["SECRET_KEY"] = token_bytes(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .series_views import series_views
    from .chapter_views import chapter_views
    from .payperiod_views import payperiod_views
    from .auth import auth

    app.register_blueprint(series_views, url_prefix="/")
    app.register_blueprint(chapter_views, url_prefix="/")
    app.register_blueprint(payperiod_views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    db.create_all(app=app)

    login_manger = LoginManager()
    login_manger.login_view = "auth.login"
    login_manger.login_message = "Please log in first. If you do not have an account, please ask to Admins."
    login_manger.init_app(app)

    @login_manger.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
