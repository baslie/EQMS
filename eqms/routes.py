from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
from sqlmodel import Session, select
from .models import Building, User
from passlib.hash import bcrypt

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)


def get_session(engine):
    return Session(engine)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with get_session(current_app.engine) as session:
            stmt = select(User).where(User.username == username)
            user = session.exec(stmt).first()
        if user and bcrypt.verify(password, user.password_hash):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Неверные имя пользователя или пароль', 'error')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@main_bp.route('/')
@login_required

def index():
    with get_session(current_app.engine) as session:
        buildings = session.exec(select(Building)).all()
    return render_template('index.html', buildings=buildings)


@main_bp.route('/buildings', methods=['POST'])
@login_required
def add_building():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('main.index'))
    if current_user.role != 'admin':
        flash('Недостаточно прав', 'error')
        return redirect(url_for('main.index'))
    with get_session(current_app.engine) as session:
        building = Building(name=name)
        session.add(building)
        session.commit()
        session.refresh(building)
    if request.headers.get('HX-Request'):
        return render_template('partials/building.html', building=building)
    return redirect(url_for('main.index'))
