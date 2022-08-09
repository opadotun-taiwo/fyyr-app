#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from wtforms.validators import ValidationError, DataRequired, Length
from sqlalchemy import false
from forms import *
from flask_migrate import Migrate
import sys
import datetime
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://USER:bolanle21@localhost:5432/dbfyyurproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  city_state_venues = Venue.query.distinct(Venue.city, Venue.state).all()
  venues_we_want = []
  #
  for area in city_state_venues:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
        venue_data.append({
            "id": venue.id,
            "name": venue.name,
        })
    venues_we_want.append({
        "city": area.city,
        "state": area.state,
        "venues": venue_data
    })
  
  return render_template('pages/venues.html', areas=venues_we_want);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  #
  query = request.form['search_term']
  search_results = Venue.query.filter(Venue.name.ilike('%' + query + '%')).all()

  venues = []
  # 
  for v in search_results:
    upcoming_shows = []
    upcoming_shows = Show.query.filter(Show.venue_id == v.id).filter(Show.start_time > datetime.datetime.today()).all()
    # 
    current = {
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": len(upcoming_shows),
    }
    venues.append(current)

  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #
  ven = Venue.query.get(venue_id)
  if ven == None:
    abort(404)
  #
  og_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.datetime.today()).all()
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.datetime.today()).count()
  #
  og_past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.datetime.today()).all()
  past_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.datetime.today()).count()
  # 
  upcoming_shows = []
  past_shows = []
  #
  for show in og_upcoming_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    upcoming_shows.append(temp)
  for show in og_past_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    past_shows.append(temp)
 
  data = {
    "id": ven.id,
    "name": ven.name,
    "genres": ven.genres,
    "city": ven.city,
    "phone":ven.phone,
    "state": ven.state,
    "address": ven.address,
    "website": ven.website_link,
    "facebook_link": ven.facebook_link,
    "image_link": ven.image_link,
    "seeking_talent": ven.seeking_talent,
    "seeking_description": ven.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count":upcoming_shows_count,
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
 

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  print(request.form)
  form = VenueForm()
  if form.validate_on_submit():
        return f'''<h1> {form.name.data} you need to adjust your input </h1>'''
  else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
  error= False
  try:
      new_venue = Venue(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        address = request.form['address'],
        phone = request.form['phone'],
        facebook_link = request.form['facebook_link'],
        website_link = request.form['website_link'],
        image_link = request.form['image_link'],
        genres = request.form.getlist('genres'),
        seeking_talent = form.seeking_talent.data,
        seeking_description = request.form['seeking_description'],
        )
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except: 
      db.session.rollback()
      flash('An error occured. Venue' + 'could not be listed')
      print(sys.exc_info())
      error = True
  finally:
      db.session.close()
  
  return render_template('pages/home.html')

  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #
  error = False
  try:
    v = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(v)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash("Failed to delete venue")
 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists', methods=['GET'])
def artists():
  # TODO: replace with real data returned from querying the database
   #
  artists = Artist.query.all()
  artist_data = []
  for art in artists:
    artist_data.append({
      "id": art.id,
      "name": art.name,
    })

  return render_template('pages/artists.html', artists=artist_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #
  query = request.form['search_term']
  search_results = Artist.query.filter(Artist.name.ilike('%' + query + '%')).all()
  #
  artists = []
  # 
  for art in search_results:
    #
    upcoming_shows = []
    upcoming_shows = Show.query.filter(Show.artist_id == art.id).filter(Show.start_time > datetime.datetime.today()).all()
    # 
    current = {
      "id": art.id,
      "name": art.name,
      "num_upcoming_shows": len(upcoming_shows),
    }
    artists.append(current)
  
  response={
    "count": len(search_results),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  #
  a = Artist.query.get(artist_id)
  if a == None:
    abort(404)

  #
  og_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.datetime.today()).all()
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.datetime.today()).count()
  #
  og_past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.datetime.today()).all()
  past_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.datetime.today()).count()
  # 
  upcoming_shows = []
  past_shows = []
  #
  for show in og_upcoming_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "venue_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    upcoming_shows.append(temp)
  for show in og_past_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "venue_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    past_shows.append(temp)
 
  data = {
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "phone":a.phone,
    "state": a.state,
    "website": a.website_link,
    "facebook_link": a.facebook_link,
    "image_link": a.image_link,
    "seeking_venue": a.seeking_venue,
    "seeking_description": a.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count":upcoming_shows_count,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  print(request.form)
  form = ArtistForm()
  if form.validate_on_submit():
        return f'''<h1> {form.name.data} you need to adjust your input </h1>'''
  else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
  error= False
  #if form.validate():
  try:
      new_artist = Artist(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        image_link = request.form['image_link'],
        genres = request.form.getlist('genres'),
        facebook_link = request.form['facebook_link'],
        website_link = request.form['website_link'],
        seeking_venue = form.seeking_venue.data,
        seeking_description = request.form['seeking_description'],
      )
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except: 
      db.session.rollback()
      flash('An error occured. Artist' + 'could not be listed')
      print(sys.exc_info())
      error= True
  finally:
      db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # select all shows from the db
  shows = Show.query.all()
  data = []
  # convert them into objects like mock data
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  if form.validate():
    try:
      new_show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data,
      )
      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except: 
      db.session.rollback()
      flash('An error occured. Artist' + 'could not be listed')
    finally:
      db.session.close()
      
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
