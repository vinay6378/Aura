# main/routes.py
from flask import Blueprint, render_template,request, redirect, url_for, flash
from models import ContactMessage, CareerApplication, Event
from extensions import db

bp = Blueprint('main', __name__, template_folder='../templates')

@bp.route('/')
def index():
    return render_template("index.html", title="Aura — One Company. Three Superpowers.")

@bp.route('/about')
def about():
    return render_template("about.html", title="About Us")

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Save to database
        new_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')

@bp.route('/events')
def events():
    events = Event.query.all()
    return render_template("events.html", events=events)

@bp.route('/webdev')
def webdev():
    return render_template("webdev.html", title="Web Development")

@bp.route('/software')
def software():
    return render_template("software.html", title="Software Development")

@bp.route('/marketing')
def marketing():
    return render_template("marketing.html", title="Marketing Services")

# Digital Marketing Specific Routes
@bp.route('/seo')
def seo():
    return render_template("seo.html", title="SEO Services")

@bp.route('/social-media')
def social_media():
    return render_template("social_media.html", title="Social Media Marketing")

@bp.route('/ppc')
def ppc():
    return render_template("ppc.html", title="PPC & Google Ads")

@bp.route('/content-marketing')
def content_marketing():
    return render_template("content_marketing.html", title="Content Marketing")

@bp.route('/marketing-analytics')
def marketing_analytics():
    return render_template("marketing_analytics.html", title="Marketing Analytics")

@bp.route('/services')
def services():
    return render_template("services.html", title="Our Services")

@bp.route('/career', methods=['GET', 'POST'])
def career():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        position_type = request.form.get("position_type")
        department = request.form.get("department")
        message = request.form.get("message")

        new_application = CareerApplication(
            name=name,
            email=email,
            position_type=position_type,
            department=department,
            message=message
        )
        db.session.add(new_application)
        db.session.commit()

        flash("Your application has been submitted successfully!", "success")
        return redirect(url_for("main.career"))

    return render_template("career.html")