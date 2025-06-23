from flask import Flask
from flask_login import LoginManager
from .models import SQLModel, User
from sqlmodel import create_engine, Session, select
from .routes import main_bp, auth_bp
from passlib.hash import bcrypt

def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'change-me'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///eqms.db'
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    SQLModel.metadata.create_all(engine)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        with Session(engine) as session:
            return session.get(User, int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.engine = engine

    # Создаем учетную запись администратора по умолчанию
    with Session(engine) as session:
        stmt = select(User).where(User.username == 'admin')
        admin = session.exec(stmt).first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=bcrypt.hash('admin'),
                role='admin'
            )
            session.add(admin)
            session.commit()

    return app