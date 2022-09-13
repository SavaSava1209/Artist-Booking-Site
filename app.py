#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser;
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# app.config.from_object('config')
setup_db(app)
# db_drop_and_create_all()
migrate = Migrate(app, db)

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

@app.route('/venues')
def venues():
  data = []
  results = Venue.query.distinct(Venue.city, Venue.state).all()
  for result in results:
    city_state_unit = {
      "city": result.city,
      "state": result.state
    }
    venues = Venue.query.filter_by(city = result.city, state=result.state).all()

    cities_venues = []
    for venue in venues:
      cities_venues.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
      })
    city_state_unit['venues'] = cities_venues
    data.append(city_state_unit)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }
  # ]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', "")
  response = {}
  venues = list(Venue.query.filter(
    Venue.name.ilike(f"%{search_term}%") |
    Venue.city.ilike(f"%{search_term}%") |
    Venue.state.ilike(f"%{search_term}%") 
  ).all())
  
  response["count"] = len(venues)
  response["data"] = []
  for venue in venues:
    venue_unit = {
      "id": venue.id,
      "name": venue.name, 
      "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
    }
    response['data'].append(venue_unit)
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = []
  venue = Venue.query.get(venue_id)
  setattr(venue, "genres", venue.genres.split(','))

  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
    temp = {}
    temp["artist_name"] = show.artists.name
    temp["artist_id"] = show.artists.id
    temp["artist_image_link"] = show.artists.image_link
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    if show.start_time < datetime.now():
      past_shows.append(temp)
    else:
      upcoming_shows.append(temp)

  setattr(venue, "past_shows", past_shows)
  setattr(venue,"past_shows_count", len(past_shows))
  setattr(venue, "upcoming_shows", upcoming_shows)
  setattr(venue,"upcoming_shows_count", len(upcoming_shows))

  return render_template('pages/show_venue.html', venue=venue)

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
  # ([('name', '123'), ('city', 'fds'), ('state', 'AL')] a tuple list
  form = VenueForm(request.form)
  if form.validate():
    try:
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = ','.join(form.genres.data),
        facebook_link = form.facebook_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data,
        website = form.website_link.data
      )
      # new_venue = <Venue id=None name=123 city=fds state=fds>
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + ' could not be listed.')
    finally:
      db.session.close()
  else:
    print("\n\n", form.errors)
    flash('An error occurred. Venue ' + ' could not be listed.')

  return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue was deleted successfully.")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Venue was not deleted successfully.")
  finally:
    db.session.close()
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  artists = Artist.query.all()
  data = []
  for artist in artists:
    temp = {}
    temp['id'] = artist.id
    temp['name'] = artist.name
    data.append(temp)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term = request.form.get('search_term', "")
  artists = Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%") |
    Artist.state.ilike(f"%{search_term}%") |
    Artist.city.ilike(f"%{search_term}%") 
  ).all()
  response = {
    "count": len(artists),
    "data": []
  }

  for artist in artists:
    temp = {}
    temp['name'] = artist.name
    temp["id"] = artist.id

    upcoming_shows = 0
    for show in artist.shows:
      if show.start_time > datetime.now():
        upcoming_shows += 1

    temp["num_upcoming_shows"] = upcoming_shows
    response["data"].append(temp) 
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):  
  artist = Artist.query.get(artist_id)
  setattr(artist, "genres", artist.genres.split(','))

  # upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), artist.shows))
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:    
    temp = {}
    temp["venue_name"] = show.venues.name
    temp["venue_image_link"] = show.venues.image_link
    temp["venue_id"] = show.venues.id
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    if show.start_time > datetime.now():
      upcoming_shows.append(temp)
    else:
      past_shows.append(temp)
    
  setattr(artist, "upcoming_shows", upcoming_shows)
  setattr(artist, 'upcoming_shows_count', len(upcoming_shows)) 
  setattr(artist, "past_shows", past_shows)
  setattr(artist, 'past_shows_count', len(past_shows)) 

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(",")
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # artist={
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "genres": ["Rock n Roll"],
  #     "city": "San Francisco",
  #     "state": "CA",
  #     "phone": "326-123-5000",
  #     "website": "https://www.gunsnpetalsband.com",
  #     "facebook_link": "https://www.facebook.com/GunsNPetals",
  #     "seeking_venue": True,
  #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  #   }

  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres=",".join(form.genres.data) # convert array to string separated by commas
      artist.facebook_link=form.facebook_link.data
      artist.image_link=form.image_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      artist.website = form.website_link.data
  
      db.session.commit()
      flash("Artist " + artist.name + " was successfully edited")
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Artist was not successfully edited")
    finally:
      db.session.close()
  else:
    print("\n\n", form.errors)
    flash("Artist was not edited successfully.")
  return redirect(url_for('show_artist', artist_id = artist_id))

@app.route('/venues/<int:venue_id>', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(",")
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.address=form.address.data
      venue.phone=form.phone.data
      venue.genres=",".join(form.genres.data) # convert array to string separated by commas
      venue.facebook_link=form.facebook_link.data
      venue.image_link=form.image_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      venue.website=form.website.data

      db.session.add(venue)
      db.session.commit()

      flash("Venue " + form.name.data + " edited successfully")
        
    except Exception:
      db.session.rollback()
      print(sys.exc_info())
      flash("Venue was not edited successfully.")
    finally:
      db.session.close()
  else: 
      print("\n\n", form.errors)
      flash("Venue was not edited successfully.")

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.validate():
    try:
       # on successful db insert, flash success
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = ",".join(form.genres.data), # convert array to string separated by commas
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data,
      )
    
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('Artist was not successfully listed!')
    finally:
      db.session.close()
  else:
    print(form.errors)
    flash('Artist was not successfully listed!')
  
  return render_template('pages/home.html')


#  delete Artist
#  ----------------------------------------------------------------
@app.route("/artists/<artist_id>/delete", methods=["post"])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash("Artist " + artist.name+ " was deleted successfully!")

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Artist was not deleted successfully!")

  finally:
    db.session.close()

  return redirect(url_for("index"))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()
  for show in shows:
    temp = {}
    temp["venue_id"] = show.venues.id
    temp["venue_name"] = show.venues.name
    temp["artist_id"] = show.artists.id
    temp["artist_name"] = show.artists.name
    temp["artist_image_link"] = show.artists.image_link
    temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    data.append(temp)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  if form.validate():
    try:
      new_show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Show was not successfully listed.')
    finally:
      db.session.close()
  else:
      print(form.errors)
      flash('Show was not successfully listed.')

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
