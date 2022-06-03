from email.policy import default
import json
import dateutil.parser
import babel
from sqlalchemy.orm.exc import NoResultFound
import traceback
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show
import sys
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate() 
migrate.init_app(app, db)


# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
    unique_city_states = Venue.query.distinct(Venue.city, Venue.state).all()
    
    data = []

    for area in unique_city_states:
        area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
        venue_data = []
        for venue in area_venues:
            venue_data.append({
                "id": venue.id,
                "name": venue.name, 
                "num_upcoming_shows": len(db.session.query(Show).filter(Show.start_time>datetime.now()).all())
            })
            data.append({
            "city": area.city,
            "state": area.state, 
            "venues": venue_data
            })

    return render_template('pages/venues.html', areas=data);



@app.route('/venues/search', methods=['POST'])
def search_venues():
    
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    find_words = request.form.get('search_term', None)
    locations= Venue.query.filter(Venue.name.ilike("%{}".format(find_words))).order_by('name').all()
    items = []
    for row in locations:
        x = {
        "id": row.id,
        "name": row.name,
        "num_upcoming_shows": len(row.shows)
        }
        items.append(x)

    response={
        "count": len(items),
        "data": items
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venues = Venue.query.filter(Venue.id == venue_id).one_or_none()
    if venues is None:
        abort(404)

    return render_template('pages/show_venue.html', venue=venues)

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
  forms_for_venue = VenueForm(request.form)
  newV = request.form.get
  if forms_for_venue.validate():
    try:
      new_venue = Venue(
          name=newV('name'),
          genres= request.form.getlist('genres'),
          address=newV('city'),
          city=newV('state'),
          phone=newV('phone'),
          facebook_link=newV('facebook_link'),
          image_link=newV('image_link'),
          seeking_talent =  True if 'seeking_talent' in request.form else False,
          seeking_description = newV('seeking_description'),
          website_link = newV('website_link')
          )
      db.session.add(new_venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except Exception as exe:
          flash('An error identified. Venue ' + request.form['name'] + ' could not be on the list' )
          print(exe)
          db.session.rollback()
    finally:
      db.session.close()
  else: 
    for field, message in forms_for_venue.errors.items():
        flash(field + ' - ' + str(message), 'danger')
        
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        remove_venue= Venue.query.filter(Venue.id == venue_id).one()
        db.session.delete(remove_venue)
        db.session.commit()
        
        flash("Venue {0} has been deleted successfully".format(remove_venue[0]['name']
        ))
    except NoResultFound:
        db.session.close()
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  search = "%{}%".format(search_term.replace(" ", "\ "))
  data = Artist.query.filter(Artist.name.match(search)).order_by('name').all()
  items = []
  for row in data:
    aux = {
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows": len(row.shows)
    }
    items.append(aux)
  response={
    "count": len(items),
    "data": items
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.filter_by(id=artist_id).first()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.genres.data = json.dumps(artist.genres)
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.website_link.data = artist.website_link
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  # return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    request_data = request.form.get
    
    if form.validate():
        artist = Artist.query.filter_by(id=artist_id).one()
        artist.name = form.name.data
        artist.genres = request.form.getlist('genres')
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = True if 'seeking_venue' in request.form else False
        artist.seeking_description = form.seeking_description.data
  
        db.session.commit()
        flash('Artist '+ request.form['name']+ ' was successfully updated')
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'error')
            db.session.rollback()
            db.session.close()
     

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venue_form = VenueForm()
    include_venue = Venue.query.get(venue_id)
    
    venue_form.name.data = include_venue.name
    venue_form.city.data = include_venue.city
    venue_form.state.data = include_venue.state
    venue_form.phone.data = include_venue.phone
    venue_form.address.data = include_venue.address
    venue_form.facebook_link.data = include_venue.facebook_link
    venue_form.website_link.data = include_venue.website_link
    venue_form.image_link.data = include_venue.image_link
    venue_form.seeking_description.data = include_venue.seeking_description
    venue_form.genres.data = json.dumps(include_venue.genres)
    
    return render_template('forms/edit_venue.html', form=venue_form, venue=include_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    if form.validate():
          venue = Venue.query.filter(Venue.id==venue_id).one()
          venue.name=form.name.data
          venue.genres= ','.join(form.genres.data)
          venue.address=form.city.data
          venue.city=form.state.data
          venue.phone=form.phone.data
          venue.facebook_link=form.facebook_link.data
          venue.image_link=form.image_link.data
          venue.seeking_talent = True if 'seeking_talent' in request.form else False
          venue.seeking_description = form.seeking_description.data
          venue.website_link = form.website_link.data
          
          db.session.commit()
          
          flash('Venue '+ request.form['name'] + ' was successfully updated')

    else: 
        for field, message in form.errors.items():
          flash(field + ' - ' + str(message), 'error')
          db.session.rollback()
          db.session.close()
      
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
    artist_form = ArtistForm(request.form)
    newA = request.form.get
    if artist_form.validate():
      try:
          new_artist = Artist(
                    name = newA('name'),
                    genres = ','.join(request.form.getlist('genres')),
                    city = newA('city'),
                    state = newA('state'),
                    phone = newA('phone'),
                    facebook_link = newA('facebook_link'),
                    image_link = newA('image_link'),
                    seeking_venue = True if 'seeking_venue' in request.form else False,
                    seeking_description = newA('seeking_description'),
                    website_link = newA('website_link')
                    )
          db.session.add(new_artist)
          db.session.commit()
          # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except Exception as exe:
          flash('An error observed. Artist '+ request.form['name'] +' could not be on the list')
          print(exe)
          db.session.rollback()
      finally:
          db.session.close()
    else: 
        for field, message in artist_form.errors.items():
          flash(field + ' - ' + str(message), 'error')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  rows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).all()
  data = []
  for row in rows:
    item = {
      'venue_id': row.Venue.id,
      'artist_id': row.Artist.id,
      'venue_name': row.Venue.name,
      'artist_name': row.Artist.name,
      'artist_image_link': row.Artist.image_link,
      'start_time': row.Show.start_time.strftime('%Y-%m-%d %H:%I')
    }
    data.append(item)
  
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
    show_form = ShowForm(request.form)
    try:
        show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
        traceback.print_exc()

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
    app.debug  = True
    app.run()