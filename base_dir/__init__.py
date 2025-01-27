from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'd26cc1dff7f27f02b85933b35410b08178201c7b58013eb842ccb67f6cfad3b3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cdo.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'acesso'
login_manager.login_message = 'Faça o Login para continuar'
login_manager.login_message_category = 'alert-info'

from base_dir import routes 
