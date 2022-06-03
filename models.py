from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)


    def __repr__(self):
        return f"<venue_id={ self.id} \
                name= {self.name} \
                genres= {self.genres.split(',')} \
                city= {self.city} \
                state= {self.state} \
                phone= {self.phone} \
                address= {self.address} \
                image_link= {self.image_link} \
                facebook_link= {self.facebook_link} \
                website= {self.website} \
                seeking_talent= {self.seeking_talent} \
                seeking_description= {self.seeking_description} \
                shows= {self.shows}>"
 
            
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist= {self.id}\
                    name= {self.name}\
                    city= {self.city}\
                    state= {self.state}\
                    phone= {self.phone}\
                    genres= {self.genres}\
                    image_link= {self.image_link}\
                    facebook_link ={self.facebook_link}\
                    website_link ={self.website_link}\
                    shows= {self.shows}>'


    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id},artist_id: {self.artist_id}, venue_id: {self.venue_id}, start_time: {self.start_time}>'