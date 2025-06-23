from flask import Flask
from .models import SQLModel
from sqlmodel import create_engine
from .routes import main_bp


def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///eqms.db'
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    SQLModel.metadata.create_all(engine)

    app.register_blueprint(main_bp)
    app.engine = engine
    return app

