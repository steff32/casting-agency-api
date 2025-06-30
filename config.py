import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://stefani.genkova:@localhost:5432/casting_agency')
SQLALCHEMY_TRACK_MODIFICATIONS = False

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'dev-tcmculz33ufggfvb.us.auth0.com')
ALGORITHMS = os.getenv('ALGORITHMS', ['RS256'])
API_AUDIENCE = os.getenv('API_AUDIENCE', 'agency') 