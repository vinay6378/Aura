from flask import Blueprint, render_template

bp = Blueprint('marketing', __name__, template_folder='../templates')

@bp.route('/')
def marketing():
    return render_template('marketing.html', title="Marketing Services")

@bp.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us")
