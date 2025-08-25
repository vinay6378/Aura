from flask import Blueprint, render_template

bp = Blueprint('dev', __name__, template_folder='../templates')

@bp.route('/')
def dev():
    return render_template('webdev.html', title="Development Services")

@bp.route('/services')
def services():
    return render_template('services.html', title="Our Services")
