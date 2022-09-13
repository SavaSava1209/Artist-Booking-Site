import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime 

database_name = "fyyur"
database_path = f'postgresql://postgres:jin@localhost:5432/{database_name}'

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)



def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    # add one demo row which is helping in POSTMAN test
    venue = Venue(
        name = "The Musical Hop",
        genres = "Jazz,Reggae,Swing,Classical,Folk",
        address = "1015 Folsom Street",
        city = "San Francisco",
        state = "CA",
        phone = "123-123-1234",
        website = "https://www.themusicalhop.com",
        facebook_link = "https://www.facebook.com/TheMusicalHop",
        seeking_talent = True,
        seeking_description = "We are on the lookout for a local artist to play every two weeks. Please call us.",
        image_link = "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    )
    venue.insert()
    artist = Artist(
        name = "Guns N Petals",
        genres = "Rock n Roll",
        city = "San Francisco",
        state = "CA",
        phone = "326-123-5000",
        website = "https://www.gunsnpetalsband.com",
        facebook_link = "https://www.facebook.com/GunsNPetals",
        seeking_venue = True,
        seeking_description = "Looking for shows to perform at in the San Francisco Bay Area!",
        image_link = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    )
    artist.insert()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="venues", lazy=False, cascade="all, delete-orphan")

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name} city={self.city} state={self.city}> \n"


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="artists", lazy=False, cascade="all, delete-orphan")

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name} city={self.city} state={self.city}> \n"

class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def insert(self):
        db.session.add(self)
        db.session.commit()