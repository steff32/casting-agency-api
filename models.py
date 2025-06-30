from flask_sqlalchemy import SQLAlchemy
import os

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()
database_path = os.getenv('DATABASE_URL', 'postgresql://stefani.genkova@localhost:5432/casting_agency')


def setup_db(app):
    with app.app_context():
        app.config["SQLALCHEMY_DATABASE_URI"] = database_path
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.app = app
        db.init_app(app)
        db.create_all()


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    # add one demo row which is helping in POSTMAN test
    movie = Movie(
        id = 1,
        title='La La Land',
        release_date='2016-12-30'
    )
    actor = Actor(
        id = 1,
        name = 'Ryan Gosling',
        age = 44,
        gender = 'male'
    )
    movie.insert()
    actor.insert()


'''
Extend the base Model class to add common methods
'''
class inheritedClassName(db.Model) :
    __abstract__ = True
    def insert(self):
        db.session.add(self)
        db.session. commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

'''
Movie
'''
class Movie(inheritedClassName):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return {"id": self.id, "title": self.title, "release_date": self.release_date.isoformat()}


'''
Actor
'''
class Actor(inheritedClassName):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return {"id": self.id, "name": self.name, "age": self.age, "gender": self.gender}