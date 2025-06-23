from flask import Blueprint, render_template, request, redirect, url_for, current_app
from sqlmodel import Session, select
from .models import Building

main_bp = Blueprint('main', __name__)


def get_session(engine):
    return Session(engine)


@main_bp.route('/')
def index():
    with get_session(current_app.engine) as session:
        buildings = session.exec(select(Building)).all()
    return render_template('index.html', buildings=buildings)


@main_bp.route('/buildings', methods=['POST'])
def add_building():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('main.index'))
    with get_session(current_app.engine) as session:
        building = Building(name=name)
        session.add(building)
        session.commit()
        session.refresh(building)
    if request.headers.get('HX-Request'):
        return render_template('partials/building.html', building=building)
    return redirect(url_for('main.index'))
