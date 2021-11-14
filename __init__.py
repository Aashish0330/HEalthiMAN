from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
import os

db = SQLAlchemy()
app = Flask(__name__, template_folder='templates')
    
def create_app():

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = os.environ.get("OAUTHLIB_INSECURE_TRANSPORT")
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQL_DB_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get("SQL_TRACK")
    app.config["DISCORD_CLIENT_ID"] = os.environ.get("DISCORD_CLIENT_ID")
    app.config["DISCORD_CLIENT_SECRET"] = os.environ.get("DISCORD_CLIENT_SECRET")            
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    db.init_app(app)
    
    with app.app_context():

        from .models import User
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        db.create_all()
        return app