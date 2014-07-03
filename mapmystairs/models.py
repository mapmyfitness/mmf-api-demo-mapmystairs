"""
    Models
    ~~~~~~
    Basic Models for the MapMyStairs Gamification Engine built on top of 
    the MapMyFitness VX API
"""
from mapmystairs import db


# Models
class Organization(db.Model):
    """
    If multiple organizations want to track their leader boards separately
    or if organizations in the same building want to compete
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Organization: %r>' % self.name


class Stairwell(db.Model):
    """
    The leaderboard is built around a single Stairwell.
    
    TODO: investigate creating 'Floors' however number of steps between
    floors can get complicated. Stay simple now.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    
    # location
    city = db.Column(db.String(80))
    state = db.Column(db.String(2))
    country = db.Column(db.String(2))
    postal_code = db.Column(db.String(20))
    
    # stats
    number_of_floors = db.Column(db.Integer)
    number_of_steps = db.Column(db.Integer)

    def __init__(self, name, city, state, country, postal_code,
                 number_of_floors, number_of_steps):
        self.name = name
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.number_of_floors = number_of_floors
        self.number_of_steps = number_of_steps
        
    def __repr__(self):
        return '<StairWell: %r in %r>' % (self.name, self.city)

        
class User(db.Model):
    """
    Local representation of the MMF User
    """
    id = db.Column(db.Integer, primary_key=True)  # is the mmf.user.id
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    time_zone = db.Column(db.String(50))
    
    # organization
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization',
                                      backref=db.backref('users'))
    
    # mmf oauth params
    oauth_token = db.Column(db.String(255))
    oauth_token_secret = db.Column(db.String(255))
    
    def __init__(self, id, username, email, first_name, last_name,
                 time_zone, organization_id, 
                 oauth_token, oauth_token_secret):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.time_zone = time_zone
        self.organization_id = organization_id
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        

    def __repr__(self):
        return '<User: %r>' % self.username


class Workout(db.Model):
    """
    Local Representation of the MMF Workout which is tied to a 
    Stairwell and direction (up vs. down)
    """
    id = db.Column(db.Integer, primary_key=True)  # is the mmf.workout.id
    workout_date = db.Column(db.DateTime)
    
    # user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", 
        backref=db.backref('workouts', order_by=id))
    
    # workout details
    time_taken = db.Column(db.Integer)
    number_of_steps = db.Column(db.Integer)
    energy_burned = db.Column(db.Integer)
    
    # stairwell
    stairwell_id = db.Column(db.Integer, db.ForeignKey('stairwell.id'))
    stairwell = db.relationship("Stairwell", 
        backref=db.backref('workouts', order_by=id))
    direction = db.Column(db.String(5))  # ie., up, down
    
    # methods
    def __init__(self, id, workout_date, user_id,
                 time_taken, number_of_steps, energy_burned,
                 stairwell_id, direction):
        
        self.id = id
        self.workout_date = workout_date
        self.user_id = user_id
        self.time_taken = time_taken
        self.number_of_steps = number_of_steps
        self.energy_burned = energy_burned
        self.stairwell_id = stairwell_id
        self.direction = direction
    
    def __repr__(self):
        return '<Workout: %s on %s>' % (self.stairwell.name, self.workout_date)

