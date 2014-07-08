"""
    Miscellenous Utils
    ~~~~~~~~~~~~~~~~~~
"""
from flask import flash, request
from sqlalchemy.sql import func

from mapmystairs import cache, db


# functions
def get_leaderboard(stairwell_id):
    """
    Get the leaderboard for a stairwell
    """
    # cache_key
    cache_key = "leaderboard-%s" % stairwell_id
    
    # clear cache
    if request.args.get("_clear_cache"):
        flash('Leaderboard Cache Cleared!', category='info')
        cache.delete(cache_key)
        
    # check cache
    leaderboard = cache.get(cache_key)
    
    if not leaderboard:
        
        # fastest up
        fastest_up_workout = None
        sql_fastest_workout = """
            SELECT 
                u.id as user_id, u.first_name, u.last_name,
                w.workout_date,
                w.time_taken, w.energy_burned, w.number_of_steps
            FROM
                workout w
                INNER JOIN user u ON u.id = w.user_id
            WHERE
                w.stairwell_id = 1 AND
                w.direction = 'up'
            ORDER BY
                w.time_taken ASC
            LIMIT 1;
            """
        results = db.engine.execute(sql_fastest_workout)
        for r in results:
            fastest_up_workout = {
                'user_id': r[0],
                'first_name': r[1],
                'last_name': r[2],
                'workout_date': r[3],
                'time_taken': r[4],
                'energy_burned': r[5],
                'number_of_steps': r[6]
            }
            
        # fastest down
        fastest_down_workout = None
        sql_fastest_workout = """
            SELECT 
                u.id as user_id, u.first_name, u.last_name,
                w.workout_date,
                w.time_taken, w.energy_burned, w.number_of_steps
            FROM
                workout w
                INNER JOIN user u ON u.id = w.user_id
            WHERE
                w.stairwell_id = 1 AND
                w.direction = 'down'
            ORDER BY
                w.time_taken ASC
            LIMIT 1;
            """
        results = db.engine.execute(sql_fastest_workout)
        for r in results:
            fastest_down_workout = {
                'user_id': r[0],
                'first_name': r[1],
                'last_name': r[2],
                'workout_date': r[3],
                'time_taken': r[4],
                'energy_burned': r[5],
                'number_of_steps': r[6]
            }
            
        # get leaderboard list
        leaderboard_list = []
        sql_leaderboard_list = """
            SELECT 
                u.id as user_id, u.first_name, u.last_name, w.direction,
                COUNT(w.id) as workout_count,
                MIN(w.time_taken) as min_time_taken,
                SUM(w.energy_burned) as total_energy_burned,
                SUM(w.number_of_steps) as total_number_of_steps
            FROM
                workout w
                INNER JOIN user u ON u.id = w.user_id
            WHERE
                w.stairwell_id = 1
            GROUP BY
                u.id, w.direction
            ORDER BY
                SUM(w.number_of_steps) DESC;
            """
        
        results = db.engine.execute(sql_leaderboard_list)
        for r in results:
            leaderboard_list.append({
                'user_id': r[0],
                'first_name': r[1],
                'last_name': r[2],
                'direction': r[3],
                'workout_count': r[4],
                'min_time_taken': r[5],
                'total_energy_burned': r[6],
                'total_number_of_steps': r[7]
                })
  
        # set leaderboard
        leaderboard = {
            'fastest_up': fastest_up_workout,
            'fastest_down': fastest_down_workout,
            'list': leaderboard_list
            }

        # set cache
        cache.set(cache_key, leaderboard, timeout=(5))  # 5s
    
    # return
    return leaderboard
