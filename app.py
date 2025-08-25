# app.py
from flask import Flask, redirect
from extensions import db, login_manager
from flask_migrate import Migrate
from models import User   # also import Event if you need it in app.py
import os

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aura.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Flask-Migrate initialization
    migrate = Migrate(app, db)

    # Register blueprints
    from main.routes import bp as main_bp
    from auth.routes import auth_bp
    from admin.routes import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    
    @app.route('/login')
    def login_redirect():
        return redirect('/auth/login')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
