"""
    Views
    ~~~~~
"""
# system
import datetime
import itertools
import logging

# 3rd party libraries
from flask import (abort, flash, make_response, render_template, 
                   redirect, Response, request, session, url_for)
import pytz
import simplejson

# our libraries
from mapmystairs import app, db
from mapmystairs.decorators import login_required
from mapmystairs.models import Organization, Stairwell, User, Workout
from mapmystairs.mmf import MapMyFitnessAPI
from mapmystairs.utils import get_leaderboard


# logging
logger = logging.getLogger(__name__)


# views
@app.route('/about')
def about():
    """
    About Page
    """
    
    # return template
    return render_template('about.html')


@app.route('/authorize')
def auth_authorize():
    """
    On successful authorization, create access token
    """
    
    # TODO: make this more dynamic. organization
    organization_id = 1  # MMF
    
    # get token
    token_key = session.get('token_key')
    token_secret = session.get('token_secret')
    
    # get oauth verifier
    oauth_verifier = request.args.get("oauth_verifier")
    oauth_token = request.args.get("oauth_token")
    
    # get access creentials
    if token_key and token_key == oauth_token:
        
        # get credentials
        mmf = MapMyFitnessAPI(app.config['MMF_API_KEY'],
                              app.config['MMF_API_SECRET'],
                              token_key=token_key,
                              token_secret=token_secret)
        
        credentials = mmf.get_token_credentials(verifier=oauth_verifier)
    
        token_key = credentials['oauth_token'][0]
        token_secret = credentials['oauth_token_secret'][0]
        user_id = credentials['user_id'][0]
        
        # set session
        session['token_key'] = token_key
        session['token_secret'] = token_secret
        session['user_id'] = user_id
        
        # get or create user
        user_dict = None
        user = User.query.filter_by(id=user_id).first()
        
        if not user:

            # get current user
            mmf = MapMyFitnessAPI(app.config['MMF_API_KEY'],
                              app.config['MMF_API_SECRET'],
                              token_key=token_key,
                              token_secret=token_secret)
        
            mmf_user = mmf.call("/user/%s/" % user_id)
            
            # build user dict
            user_dict = {
                'id': user_id,
                'username': mmf_user['username'],
                'email': mmf_user['email'],
                'first_name': mmf_user['first_name'],
                'last_name': mmf_user['last_name'],
                'organization_id': organization_id,
                'time_zone': mmf_user['time_zone'],
                'oauth_token': token_key,
                'oauth_token_secret': token_secret
                }
            user = User(**user_dict)
            
            # add user
            db.session.add(user)
            db.session.commit()
        
        if not user_dict:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'organization_id': user.organization_id,
                'time_zone': user.time_zone,
                'oauth_token': user.oauth_token,
                'oauth_token_secret': user.oauth_token_secret
                }
            
        session['user'] = user_dict
        
        # redirect to leaderboard page
        return redirect(url_for("leaderboard"))
    
    session.clear()
    flash('Invalid Authorize', category='error')
    return redirect(url_for("index"))


@app.route('/login')
def auth_login(next=None):
    """
    Creates the VX token and redirects to auth
    """
    
    # set next
    if not next:
        next = url_for("leaderboard")
    
    # check if auth exists
    token_key = session.get('token_key')
    token_secret = session.get('token_secret')
    
    logger.debug("auth_login:token_key=%s", token_key)
    logger.debug("auth_login:token_secret=%s", token_secret)
    
    # no token -> request and authorize
    if not token_key or not token_secret:
        
        mmf = MapMyFitnessAPI(app.config['MMF_API_KEY'],
                              app.config['MMF_API_SECRET'])
        
        # get temporary credentials
        temporary_credentials = mmf.get_temporary_credentials(
                    callback_uri=url_for('auth_authorize', _external=True))
        
        # authorize
        authorize_url = temporary_credentials['authorize_url'][0]
        token_key = temporary_credentials['oauth_token'][0]
        token_secret = temporary_credentials['oauth_token_secret'][0]
        
        session['token_key'] = token_key
        session['token_secret'] = token_secret
        
        return redirect(authorize_url)
    
    return redirect(next)
    

@app.route('/logout')
def auth_logout():
    session.clear()
    flash('You were logged out', category='info')
    return redirect(url_for("index"))


@app.route('/debug')
def debug():
    """
    Returns Error to allow for Debugger
    """
    return fake_error


@app.route('/')
def index():
    """
    Main Index Page
    """
    
    # if user
    if session.get("user"):
        # redirect to leaderboard page
        return redirect(url_for("leaderboard"))
    
    # return template
    return render_template('index.html')


@app.route('/leaderboard')
@login_required
def leaderboard():
    """
    Main Leaderboard
    
    TODO: get user stairwells
    TODO: date range filter
    TODO: different sort order
    TODO: caching
    """
    
    # TODO: get user stairwells
    stairwell_id = 1
    stairwell = Stairwell.query.get(stairwell_id)
    
    # leaderboard
    leaderboard = get_leaderboard(stairwell_id)
    
    # build context
    context = {
        'stairwell': stairwell,
        'leaderboard': leaderboard
        }
    
    # return template
    return render_template('leaderboard.html', **context)


@app.route('/stairwells')
def stairwell_list():
    """
    List all Stairwells
    """
    
    # get stairwells
    stairwells = Stairwell.query.all()
    
    # build context dict
    context = {'stairwells': stairwells}
    
    # return template
    return render_template('stairwell_list.html', **context)


@app.route('/stairwell/<int:stairwell_id>')
def stairwell_view(stairwell_id):
    """
    View Stairwell Record 
    """
    
    # get stairwells
    stairwell = Stairwell.query.get(stairwell_id)
    
    # build hotlinks
    up_link = url_for('workout', stairwell_id=stairwell.id,
                      direction="up", _external=True)
    
    down_link = url_for('workout', stairwell_id=stairwell.id,
                      direction="down", _external=True)
    
    # build context dict
    context = {
               'stairwell': stairwell,
               'up_link': up_link,
               'down_link': down_link
               }
    
    # return template
    return render_template('stairwell_view.html', **context)


@app.route('/workout/<int:stairwell_id>/<direction>')
@login_required
def workout(stairwell_id, direction):
    """
    Start / Stop Stairs Workout
    """
    
    # get cancel
    cancel_flag = request.args.get("cancel_flag")
    
    # handle cancel
    if cancel_flag or cancel_flag == "True":
        
        # delete session
        session["workout"] = None
        
        # info message
        flash('Stair Climb Cancelled!', category='info')
        
        # redirect to leaderboard page
        return redirect(url_for("leaderboard"))

    # defaults
    context = {
        'stairwell_id': stairwell_id,
        'direction': direction,
        'cancel_flag': cancel_flag 
    }
    
    # check to see if existing session exists
    workout = session.get("workout")
    
    if not workout:
        
        # get stairwell
        stairwell = Stairwell.query.get(stairwell_id)

        # build workout name
        workout_name = 'walked %s %s stairs' % (direction,
                                                stairwell.number_of_steps)
        
        # build workout
        workout_start = datetime.datetime.now(pytz.utc)
        
        workout = {
            'activity_type_id': 133,
            'name': workout_name,
            'start_datetime': workout_start,
            'start_locale_timezone': session['user']['time_zone'],
            'stairwell_id': stairwell_id,
            'notes': 'climbed %s' % stairwell.name,
            'number_of_steps':  stairwell.number_of_steps,
            'direction': direction
            }
        
        session['workout'] = workout
        
    else:

        workout_start = workout["start_datetime"]
        
        # convert back to UTC as pickle lost timezone
        workout_start = datetime.datetime(workout_start.year,
                            workout_start.month, workout_start.day,
                            workout_start.hour, workout_start.minute,
                            workout_start.second, tzinfo=pytz.utc)
        
        # only save if scan the top or bottom
        if direction != workout["direction"]:
            
            now = datetime.datetime.now(pytz.utc)
            
            # delta in seconds
            active_time_total = (now - workout_start).total_seconds()
            
            # build vx workout
            fmt = '%Y-%m-%d %H:%M:%S %Z'
            vx_workout = {
                "start_datetime": workout_start.strftime(fmt),
                "name": workout["name"],
                "notes": workout.get("notes", ""),
                "privacy": "/v7.0/privacy_option/1/",
                "aggregates": {
                    "active_time_total": active_time_total,
                },
                "time_series": {
                    "steps": [[0, 0], 
                              [active_time_total, workout["number_of_steps"]]]
                },
                "start_locale_timezone": workout["start_locale_timezone"],
                "activity_type": "/v7.0/activity_type/%s/" \
                                    % workout["activity_type_id"]
                }
            
            logger.debug("vx_workout: %s", vx_workout)
            
            # api connection
            mmf = MapMyFitnessAPI(
                        app.config['MMF_API_KEY'],
                        app.config['MMF_API_SECRET'],
                        token_key=session["user"]["oauth_token"],
                        token_secret=session["user"]["oauth_token_secret"]
                        )
        
            vx_result = mmf.call("/workout/", http_method="POST",
                              data=simplejson.dumps(vx_workout))
            logger.debug("vx_result: %s", vx_result)
            
            # build workout
            tz = pytz.timezone(session["user"]["time_zone"])
            time_taken = vx_result['aggregates']['elapsed_time_total']
            energy_burned = vx_result['aggregates']\
                            .get('metabolic_energy_total', 0) * 0.000239005736
                            
            w = Workout(**{
                        'id': vx_result['_links']['self'][0]['id'], 
                        'workout_date': workout_start.astimezone(tz)\
                                            .strftime('%Y-%m-%d %H:%M:%S'),
                        'user_id': session['user']['id'],
                        'time_taken': time_taken, 
                        'number_of_steps': workout["number_of_steps"], 
                        'energy_burned': energy_burned,
                        'stairwell_id': workout["stairwell_id"],
                        'direction': workout["direction"]
                        })
            
            # add workout
            logger.debug("Saving w:%s", w)
            db.session.add(w)
            db.session.commit()
            
            session['workout'] = None
            flash('Stair Climb Saved!', category='success')
    
            # redirect to leaderboard page
            return redirect(url_for("leaderboard"))
        
    # add workout to context
    context['workout'] = workout
    
    # calculate epcoh
    workout_start_epoch = (workout_start \
                           - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc))\
                           .total_seconds()
                           
    context['workout_start_epoch'] = workout_start_epoch
    
    # return template
    return render_template('workout.html', **context)
    