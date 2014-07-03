"""
    Settings
    ~~~~~~~~
"""
import os

# "https://api.mapmyapi.com/v7.0"
MMF_API_KEY = os.environ['MMF_API_KEY']
MMF_API_SECRET = os.environ['MMF_API_SECRET']

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']