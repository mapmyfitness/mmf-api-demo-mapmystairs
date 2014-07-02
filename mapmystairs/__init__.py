"""
    MapMyStairs.com
    ~~~~~~~~~~~~~~~
"""
import logging

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import settings


# Init App
app = Flask(__name__)

# load config
app.config.from_object(settings)

# Load SqlAlchemay
db = SQLAlchemy(app)
 
# set the secret key.  keep this really secret:
app.secret_key = '001011!0 00011011 1100a111 10001111 10100101 1011y001'

# set logging
log_level = logging.DEBUG
log_format = "%(asctime)s [%(levelname)s] %(message)s:"
logging.basicConfig(format=log_format, level=log_level)

# load views
import views
