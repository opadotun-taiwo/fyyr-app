from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms.validators import ValidationError, DataRequired, Length, URL, validators, regex


db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120),validators=[DataRequired(), validators.Regexp(regex, flags=0, message="enter valid number")])
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()), nullable = False)
    facebook_link = db.Column(db.String(120), validators=[URL()])
    website_link = db.Column(db.String(120), validators=[URL()])
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    
    
    shows = db.relationship('Show', backref=db.backref('venue', lazy='joined'), lazy='joined', 
    cascade="all, delete-orphan")


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), validators=[DataRequired(), validators.Regexp(regex, flags=0, message="enter valid number")])
    genres = db.Column(db.ARRAY(db.String()), nullable = False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), validators=[URL()])
    website_link = db.Column(db.String(120), validators=[URL()])
    seeking_description = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    shows = db.relationship('Show', backref=db.backref('artist', lazy='joined'), lazy='joined', 
    cascade="all, delete-orphan")
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    