from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS



app = Flask(__name__)

app.config.from_object(Config)

CORS(app, resources={r"/api/*": {'origins': '*'}})

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login = LoginManager(app)

login.login_view = 'login'
login.login_message = 'You need to be logged in to do that.'
login.login_message_category = 'danger'


from app.blueprints.api import api
app.register_blueprint(api)

from app import models
