from flask import Blueprint, render_template

bp = Blueprint('events', __name__, template_folder='../templates')

@bp.route('/')
def events():
    return render_template('events.html', title="Events")

@bp.route('/<int:event_id>')
def event_detail(event_id):
    return render_template('event_detail.html', event_id=event_id, title="Event Details")
