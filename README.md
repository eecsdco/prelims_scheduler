prelims README
==================

This directory is a self-contained webapp built on top of Pyramid web framework,
part of the [Pylons project](www.pylonsproject.org). The goal of modern web
frameworks are to tease apart data backends (models), website logic
(controllers), and the rendered website itself (views). In practice, this means
it can be a little intimidating to see how everything goes together to build
things at first, I'll try to give a simple overview.

Updates Nov. 2021
---------------
- This project now requires Python3 to run.
- Pserve now uses 'gunicorn' instead of 'waitress' to serve up the application because gunicorn supports SSL whereas waitress does not. This dependency was added in setup.py.
- Added 'setuptools' to setup.py as it was required by Python3.
- The project is protected behind a Shibboleth login. The directory for shibboleth is /var/www/html/secure. Laura has it redirecting appropriately to <https://horton.eecs.umich.edu:6543>. 

Getting Started
---------------

The website is basically a lot of extra python modules all working together.
Web framework pieces tend to have relatively high churn without the highest
emphasis on backwards compatability, the solution is to have one python
environment for each website (a "virtualenv").


### Virtualenv

Create a virtual environment for this project:

    # venv_prelims is the name of the directory that will be created
    python -m venv venv_prelims

Next we need to "activate" this virtual environment. This is done on a
_per-shell_ basis (it will update your `$PS1` automatically). There are tools
([virtualenvwrapper](virtualenvwrapper.readthdocs.org/en/latest/index.html))
that will automate this, but are probably more than you care about.

    # Activate this virtual environment
    source venv_prelims/bin/activate

Anything python-related (e.g. install packages) you do in a virtual enivronment
will only affect this environment. This also means you don't have to (in fact,
should not) be installing things as root, since they're only being installed in
this local folder.

### Building the webapp

First we have to install all of the dependencies inside of this virtualenv. If
you add any new packages, be sure to add them to the `requires` array inside of
`setup.py`.

    # Make sure you do this in shell with the venv_prelims virtualenv active!
    python setup.py develop

The next step is to initialize the databsae. We use sqlite, which means the
database is just a simple file on disk, but this script will take care of things
like setting up all of the tables properly. It also pre-populates the faculty
table with the list found in `prelims/scripts/fac_uniqs`.

    initialize_prelims_db development.ini

> If you are developing, it may be more useful to skip this step and instead
> use the example database which is pre-populated with a little bit of test
> data. In that case, all you need to do is `cp exampledb.sqlite prelims.sqlite`

### Deploying the webapp

For basic testing / debugging, python includes a built-in http server, which is
easier than bothering to hook it in to apache / nginx / whatever your webserver
of choice is.

    pserve development.ini --reload

The `--reload` flag is optional, but is nice during development. It will cause
the site to automatically rebuild whenever you edit a file that would require a
rebuild.

If you're going to be debugging this on a remote machine, be sure to add your
local machine to the `debugtoolbar.hosts` entry in `development.ini`.

### SSL Keys

Whether running this app locally or on the server, make sure to have the following keys in place:
- /etc/ssl/certs/all.cert
- /etc/ssl/private/key.pem 

### That's it!

You should be able to visit the site at <https://0.0.0.0:6543/> locally or on horton at <http://horton.eecs.umich.edu:6543>.

