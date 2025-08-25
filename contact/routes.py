from flask import Blueprint, render_template, request, flash, redirect, url_for

contact_bp = Blueprint('contact', __name__, template_folder='../templates')

@contact_bp.route('/', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        flash(f'Thanks {name or "there"}, your message has been received.', 'success')
        return redirect(url_for('contact.contact'))
    return render_template('contact.html')
