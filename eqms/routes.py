from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
from sqlmodel import Session, select
from .models import Building, Entrance, Elevator, User
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


@main_bp.route('/buildings/<int:building_id>')
@login_required
def building_detail(building_id: int):
    with get_session(current_app.engine) as session:
        building = session.get(Building, building_id)
        if not building:
            flash('Объект не найден', 'error')
            return redirect(url_for('main.index'))
        entrances = session.exec(
            select(Entrance).where(Entrance.building_id == building_id)
        ).all()
    return render_template(
        'building_detail.html', building=building, entrances=entrances
    )


@main_bp.route('/buildings/<int:building_id>/entrances', methods=['POST'])
@login_required
def add_entrance(building_id: int):
    name = request.form.get('name')
    if not name:
        return redirect(url_for('main.building_detail', building_id=building_id))
    if current_user.role != 'admin':
        flash('Недостаточно прав', 'error')
        return redirect(url_for('main.building_detail', building_id=building_id))
    with get_session(current_app.engine) as session:
        entrance = Entrance(name=name, building_id=building_id)
        session.add(entrance)
        session.commit()
        session.refresh(entrance)
    if request.headers.get('HX-Request'):
        return render_template('partials/entrance.html', entrance=entrance)
    return redirect(url_for('main.building_detail', building_id=building_id))


@main_bp.route('/entrances/<int:entrance_id>')
@login_required
def entrance_detail(entrance_id: int):
    with get_session(current_app.engine) as session:
        entrance = session.get(Entrance, entrance_id)
        if not entrance:
            flash('Подъезд не найден', 'error')
            return redirect(url_for('main.index'))
        elevators = session.exec(
            select(Elevator).where(Elevator.entrance_id == entrance_id)
        ).all()
    return render_template(
        'entrance_detail.html', entrance=entrance, elevators=elevators
    )


@main_bp.route('/entrances/<int:entrance_id>/elevators', methods=['POST'])
@login_required
def add_elevator(entrance_id: int):
    name = request.form.get('name')
    if not name:
        return redirect(url_for('main.entrance_detail', entrance_id=entrance_id))
    if current_user.role != 'admin':
        flash('Недостаточно прав', 'error')
        return redirect(url_for('main.entrance_detail', entrance_id=entrance_id))
    with get_session(current_app.engine) as session:
        elevator = Elevator(name=name, entrance_id=entrance_id)
        session.add(elevator)
        session.commit()
        session.refresh(elevator)
    if request.headers.get('HX-Request'):
        return render_template('partials/elevator.html', elevator=elevator)
    return redirect(url_for('main.entrance_detail', entrance_id=entrance_id))
