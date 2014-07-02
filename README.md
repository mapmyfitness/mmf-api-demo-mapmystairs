mmf-api-demo-mapmystairs
========================

You can download the app here:
https://github.com/mapmyfitness/mmf-api-demo-mapmystairs

The MapMyFitness API MapMyStairs Demo is a sample web app writing in python.  
It uses the Flask framework to showcase simple gamification capabilities.

In this case, this was a game developed in July 2014 when the building we
were in put their elevator into repair mode for the hottest month in Austin, TX.
The MapMyFitness office is located on the 6th floor so we wanted to create
a simple way to track team members as they utilized the stairs on a daily
basis.

To get a MapMyFitness Developer Key visit https://developer.mapmyapi.com/

Requirements
------------
- MapMyFitness Developer Key
- pip 
- virtualenv
- mysql instance with host, database, username, password, and port.


Installation
------------

To get the code and create the virtual environment:

    $ git clone https://github.com/mapmyfitness/mmf-api-demo-mapmystairs
    $ mkvirtualenv mmf-api-demo-mapmystairs
    (mmf-api-demo-mapmystairs) $ cd mmf-api-demo-mapmystairs    
    (mmf-api-demo-mapmystairs) $ pip install --allow-all-external -r requirements.txt
    
Note:
On Mac OX you may have to modify your ~/.virtualenvs/mmf-api-demo-mapmystairs/bin/postactivate hook
{Workspace} is your workspace directory where you cloned the hmt repo.

    #!/bin/bash
    # This hook is run after this virtualenv is activated.
    export PYTHONPATH="~/.virtualenvs/mmf-api-demo-mapmystairs/lib/python2.7/site-packages"
    cd /{Workspace}/mmf-api-demo-mapmystairs

To setup your settings.py:

    $ workon mmf-api-demo-mapmystairs
    (mmf-api-demo-mapmystairs) $ cp settings.dist.py settings.py
    (mmf-api-demo-mapmystairs) $ vi settings.py   

Setting up the Database
-----------------------

Open ipython in the virtualenv and using sqlalchemy, initialize the database.

    $ workon mmf-api-demo-mapmystairs
    (mmf-api-demo-mapmystairs) $ ipython
    ...
    In [1]: from mapmystairs import db
    In [2]: from mapmystairs.models import *
    In [3]: db.create_all()

You can also create some basic starter objects using the same ipython session:

    In [4]: mmf_organization = Organization(name='MapMyFitness')
    In [5]: abc_bank_stairwell = Stairwell(
                name="ABC Bank Building",
                city="Austin", state="TX", country="us", postal_code="78701",
                number_of_floors=6, number_of_steps=65
             )
    In [6]: db.session.add(mmf_organization)
    In [7]: db.session.add(abc_bank_stairwell)
    In [8]: db.session.commit()

Run Flask Server
----------------
    
    $ workon mmf-api-demo-mapmystairs
    (mmf-api-demo-mapmystairs) $ python runserver.py


