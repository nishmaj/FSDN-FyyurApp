#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database

db = SQLAlchemy()
migrate = Migrate(app, db)

with app.app_context():
   db.init_app(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy="dynamic")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __init__(self, name, genres, address, city, state, phone, website, facebook_link, image_link,
                 seeking_talent=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.address = address
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description
        self.image_link = image_link

    def shortDisplay(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
            }


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')

    def __init__(self, name, genres, city, state, phone, image_link, website, facebook_link,
                 seeking_venue=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.image_link = image_link

    def shortDisplay(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        }

class Show(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def details_artist(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def details_venue(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time
        }


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  city_and_state = ''
  data = []

  venue_query = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()

  for venue in venue_query:
    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()

    if city_and_state == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      })
      
    else:
      city_and_state = venue.city + venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    for result in venue_query:
      venue_array = list(map(Venue.shortDisplay, venue_query))
    
    response = {
      "count": len(venue_array),
      "data": venue_array
    }
    return render_template (
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_query = Venue.query.get(venue_id)
      
    if venue_query:
      venue_details = Venue.details(venue_query)
      current_time = datetime.now().strftime('%Y-%m-%d')
      new_shows_query = Show.query.options(db.joinedload('Artist')).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
      new_show = list(map(Show.details_artist, new_shows_query))
      venue_details["upcoming_shows"] = new_show
      venue_details["upcoming_shows_count"] = len(new_show)
      past_shows_query = Show.query.options(db.joinedload('Artist')).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
      past_shows = list(map(Show.details_artist, past_shows_query))
      venue_details["past_shows"] = past_shows
      venue_details["past_shows_count"] = len(past_shows)
      
      return render_template('pages/show_venue.html', venue=venue_details)
    else:
      return render_template('errors/404.html')
  

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
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashin

  data = request.form
  try:
    new_venue = Venue(
    genres=data.getlist("genres[]"),
    name=data.get("name"),
    address=data.get("address"),
    city=data.get("city"),
    state=data.get("state"),
    facebook_link=data.get("facebook_link"),
    phone=data.get("phone"),
    website=data.get("website_link"),
    image_link=data.get("image_link")
  )

    db.session.add(new_venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except SQLAlchemyError as e:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_query = Venue.query.get(venue_id)
  
  if venue_query:
    db.session.delete(venue_query)
    db.session.commit()
  else:
    flash('An error occurred while deleting')

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_query = Artist.query.all()
  artist_map = list(map(Artist.shortDisplay, artist_query))

  return render_template('pages/artists.html', artists=artist_map)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  artist_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  artist_mapper = list(map(Artist.shortDisplay, artist_query))
  response={
    "count": len(artist_mapper),
    "data": artist_mapper
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist_query = Artist.query.get(artist_id)
  if artist_query:
        artist_details = Artist.details(artist_query)
        current_time = datetime.now().strftime('%Y-%m-%d')
        upcoming_shows_query = Show.query.options(db.joinedload('Artist')).filter(Show.artist_id == artist_id).filter(Show.start_time >= current_time).all()
        for query in upcoming_shows_query:
          print(query.id)
          print(query.artist_id)
          print(query.venue_id)
          print(query.start_time)
        upcoming_shows_list = list(map(Show.details_venue, upcoming_shows_query))
        artist_details["upcoming_shows"] = upcoming_shows_list
        artist_details["upcoming_shows_count"] = len(upcoming_shows_list)
        past_shows_query = Show.query.options(db.joinedload('Artist')).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
        past_shows_list = list(map(Show.details_venue, past_shows_query))
        artist_details["past_shows"] = past_shows_list
        artist_details["past_shows_count"] = len(past_shows_list)
        print(artist_details)
        return render_template('pages/show_artist.html', artist=artist_details)
  return render_template('errors/404.html')
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data = request.form
  artist_query = Artist.query.get(artist_id)

  if artist_query:
    artist_details = Artist.details(artist_query)
    form.name.data = artist_details["name"]
    form.genres.data = artist_details["genres"]
    form.city.data = artist_details["city"]
    form.state.data = artist_details["state"]
    form.phone.data = artist_details["phone"]
    form.facebook_link.data = artist_details["facebook_link"]
    return render_template('forms/edit_artist.html', form=form, artist=artist_details) 
  return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  artist_query = Artist.query.get(artist_id)

  if artist_query:
    setattr(artist_query, 'name', request.form.get('name'))
    setattr(artist_query, 'genres', request.form.get('genres'))
    setattr(artist_query, 'city', request.form.get('city'))
    setattr(artist_query, 'state', request.form.get('state'))
    setattr(artist_query, 'phone', request.form.get('phone'))
    setattr(artist_query, 'facebook_link', request.form.get('facebook_link'))
    db.session.commit()
    
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('Updating the form was not successful')
  return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  data = request.form
  venue_query = Venue.query.get(venue_id)

  if venue_query:
    venue_details = Venue.details(venue_query)
    form.name.data = venue_details["name"]
    form.genres.data = venue_details["genres"]
    form.address.data = venue_details["address"]
    form.city.data = venue_details["city"]
    form.state.data = venue_details["state"]
    form.phone.data = venue_details["phone"]
    form.facebook_link.data = venue_details["facebook_link"]
    return render_template('forms/edit_venue.html', form=form, venue=venue_details)
  return render_template('errors/404.html')

  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm()
  venue_query = Venue.query.get(venue_id)

  if venue_query:
    
    setattr(venue_query, 'name', request.form.get('name'))
    setattr(venue_query, 'genres', request.form.get('genres'))
    setattr(venue_query, 'city', request.form.get('city'))
    setattr(venue_query, 'state', request.form.get('state'))
    setattr(venue_query, 'address', request.form.get('address'))
    setattr(venue_query, 'phone', request.form.get('phone'))
    setattr(venue_query, 'facebook_link', request.form.get('facebook_link'))
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('errors/404.html')



  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

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

  form = ArtistForm()
  data = request.form
  try:
    seeking_venue = None
    if 'seeking_venue' in request.form:
      seeking_venue = request.form['seeking_venue'] == 'y'

    new_artist = Artist(
        name=data.get("name"),
        genres=data.getlist("genres[]"),
        city=data.get("city"),
        state=data.get("state"),
        phone=data.get("phone"),
        website=data.get("website_link"),
        seeking_venue= seeking_venue,
        facebook_link=data.get("facebook_link"),
        seeking_description=data.get("seeking_description"),
        image_link=data.get("image_link")
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows_query = Show.query.all()
  shows_mapper = list(map(Show.details, shows_query))
  data = shows_mapper

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
  data = request.form

  try:
    new_show = Show(
      venue_id=data.get('venue_id'),
      artist_id=data.get('artist_id'),
      start_time=data.get('start_time')
    )
    Show.insert(new_show)
    flash('Show was successfuly listed!')
  except SQLAlchemyError as e:
    flash('An error occured. Show could not be listed.')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
