import os
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Movie, Actor, setup_db

from auth import AuthError, requires_auth

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# This loads variables from .env into the environment, if the file exists
load_dotenv()

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  with app.app_context():
    db.create_all()

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,PATCH')
    return response


  # Routes
  @app.route('/movies', methods=['GET'])
  @requires_auth('view:movies')
  def get_movies(payload):
      movies = Movie.query.all()
      return jsonify({"success": True, "movies": [repr(m) for m in movies]}), 200


  @app.route('/actors', methods=['GET'])
  @requires_auth('view:actors')
  def get_actors(payload):
      actors = Actor.query.all()
      return jsonify({"success": True, "actors": [repr(a) for a in actors]}), 200


  @app.route('/movies', methods=['POST'])
  @requires_auth('add:movies')
  def create_movie(payload):
      data = request.get_json()
      try:
          movie = Movie(title=data['title'], release_date=data['release_date'])
          movie.insert()
          return jsonify({"success": True, "movie": repr(movie)}), 201
      except Exception:
          db.session.rollback()
          abort(422)
      finally:
          db.session.close()


  @app.route('/actors', methods=['POST'])
  @requires_auth('add:actors')
  def create_actor(payload):
      data = request.get_json()
      try:
          actor = Actor(name=data['name'], age=data['age'], gender=data['gender'])
          actor.insert()
          return jsonify({"success": True, "actor": repr(actor)}), 201
      except Exception:
          db.session.rollback()
          abort(422)
      finally:
          db.session.close()


  @app.route('/movies/<int:movie_id>', methods=['PATCH'])
  @requires_auth('update:movies')
  def update_movie(payload, movie_id):
      movie = Movie.query.get(movie_id)
      if not movie:
          abort(404)
      data = request.get_json()
      movie.title = data.get('title', movie.title)
      movie.release_date = data.get('release_date', movie.release_date)
      movie.update()
      return jsonify({"success": True, "movie": repr(movie)})


  @app.route('/actors/<int:actor_id>', methods=['PATCH'])
  @requires_auth('update:actors')
  def update_actor(payload, actor_id):
      actor = Actor.query.get(actor_id)
      if not actor:
          abort(404)
      data = request.get_json()
      actor.name = data.get('name', actor.name)
      actor.age = data.get('age', actor.age)
      actor.gender = data.get('gender', actor.gender)
      actor.update()
      return jsonify({"success": True, "actor": repr(actor)})


  @app.route('/movies/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(payload, movie_id):
      movie = Movie.query.get(movie_id)
      if not movie:
          abort(404)
      movie.delete()
      return jsonify({"success": True, "delete": movie_id})


  @app.route('/actors/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(payload, actor_id):
      actor = Actor.query.get(actor_id)
      if not actor:
          abort(404)
      actor.delete()
      return jsonify({"success": True, "delete": actor_id})


  # Error Handlers
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({"success": False, "error": 404, "message": "Resource not found"}), 404


  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({"success": False, "error": 422, "message": "Unprocessable"}), 422
  
  @app.errorhandler(AuthError)
  def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)