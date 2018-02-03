import os
from flask import Flask
from flask_assets import Environment, Bundle
from flask_pymongo import PyMongo
from hamlish_jinja import HamlishExtension


app = Flask(__name__)


class DefaultSettings:
    MONGO_HOST = 'localhost'
    DB_LOCATION = os.path.dirname(os.path.abspath(__file__))


app.config.from_object('dwcfiles.DefaultSettings')       # Development settings
app.config.from_envvar('DWCFILES_SETTINGS', silent=True) # Production settings

# Hamlish-jinja setup
app.jinja_env.add_extension(HamlishExtension)
app.jinja_env.hamlish_enable_div_shortcut = True

# Assets (Sass, JS) setup
assets = Environment(app)

# Secret key (used for CSRF protection and sessions)
# To generate, execute this in a Python 3.6+ shell:
# import secrets
# secrets.token_bytes(24)
# And save it in 'secret_key' file in instance folder
with app.open_instance_resource('secret_key') as f:
    app.secret_key = f.read()

# Connect to the MongoDB database
mongo = PyMongo(app)

import dwcfiles.views

