from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate, csrf


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    from . import models  # noqa: F401

    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .sessions import bp as sessions_bp
    from .activities import bp as activities_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(sessions_bp, url_prefix="/sessions")
    app.register_blueprint(activities_bp, url_prefix="/activities")

    from public_demo import init_public_demo
    init_public_demo(app)

    return app

