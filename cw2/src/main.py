import ConfigParser
import logging
import sqlite3
import os

from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, redirect, render_template, flash, url_for, abort, g

from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask.ext.wtf import Form

from urlparse import urlparse, urljoin
from wtforms import TextField, HiddenField
from contextlib import closing



app = Flask(__name__)




#db_location = 'var/pubstest.db'



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
  c = g.db.execute("SELECT id_user FROM user WHERE id_user = (?)", [id])
  userid =c.fetchone()
  return userid


class User(UserMixin): 

  def __init__(self,username,password,email):
    self.username = username
    self.password = password
    self.email = email

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    c = g.db.execute('SELECT id_user FROM user WHERE name_user = (?)', [self.username])
    id = c.fetchone()
    return unicode(id)

  def __repr__(self):
    return '<User %r>' % (self.username)



def init(app):
    config = ConfigParser.ConfigParser()
    config_location = "etc/config.cfg"
    try:
        config.read(config_location)

        app.config['debug'] = config.get("config", "debug")
        app.config['ip_address'] = config.get("config", "ip_address")
        app.config['port'] = config.get("config", "port")
        app.config['url'] = config.get("config", "url")

        
	app.config['database'] = config.get("config", "database")
        app.config['username'] = config.get("config", "username")
        app.config['password'] = config.get("config", "password")

        app.config['log_file'] = config.get("logging", "name")
        app.config['log_location'] = config.get("logging", "location")
        app.config['log_level'] = config.get("logging", "level")

	app.secret_key = config.get("config", "secret_key")

    except:
        print ("Could not read configs from: "), config_location

def logs(app):
    log_pathname = app.config['log_location'] + app.config['log_file']
    file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10, backupCount=1024)
    file_handler.setLevel(app.config['log_level'])
    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.setLevel(app.config['log_level'])
    app.logger.addHandler(file_handler)

def connect_db():
  init(app)
  conn = sqlite3.connect(app.config['database'])
  conn.row_factory = sqlite3.Row
  return conn

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def get_db():
  if not hasattr(g, 'sqlite_db'):
    g.sqlite_db = connect_db()
  return g.sqlite_db



@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g,'db', None)
  if db is not None:
    db.close()


def is_safe_url(target):
  ref_url = urlparse(request.host_url)
  test_url = urlparse(urljoin(request.host_url, target))
  return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc

def get_redirect_target():
  for target in request.args.get('next'), request.referrer:
    if not target:
      continue
    if is_safe_url(target):
      return target

class RedirectForm(Form):
  next = HiddenField()

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
    if not self.next.data:
      self.next.data = get_redirect_target() or ''

  def redirect(self, endpoint='base', **values):
    if is_safe_url(self.next.data):
      return redirect(self.next.data)
    target = get_redirect_target()
    return redirect(target or url_for(endpoint, **values))

class LoginForm(RedirectForm):
  username = TextField('Username')
  password = TextField('Password')


@app.route('/createaccount/', methods=['GET','POST'])
def createaccount():
  if request.method == 'GET':
    return render_template('createaccount.html')
  if request.method == 'POST':
    db = get_db()
    db.execute('INSERT INTO user (name_user, password_user, email_user) VALUES (?,?,?)',[request.form['username'],request.form['password'],request.form['email']])
    db.commit()
    flash('Your account was successfully created!')
    return render_template('login.html',previouspage="createaccount")

@app.route('/display_users')
def display_users():
  cur = g.db.cursor()
  cur = g.db.execute('SELECT id_user, name_user, email_user FROM user ORDER BY id_user ASC')
  entries = [dict(id_user=row[0],name_user=row[1], email_user=row[2]) for row in cur.fetchall()]
  return render_template('display_users.html',entries=entries, currentpage="display_users")

@app.route("/useraccount/")
@app.route("/useraccount/<name>")
def useraccount(name=None):
  return render_template('useraccount.html', name=name)


@app.route('/login', methods = ['GET','POST'])
def login():
  error = None
  form = LoginForm()
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    c = g.db.execute("SELECT name_user FROM user WHERE name_user = (?)",[username])
    userexists = c.fetchone()
    if userexists: 
      c = g.db.execute("SELECT password_user FROM user WHERE password_user = (?)", [password])
      passwcorrect = c.fetchone()
    else:
      return render_template('login.html',error = 'Invalid username')
    if passwcorrect:
      user = User(username,password,'email')
      login_user(user)
      session['logged_in'] = True 
      flash('Logged in successfully.')
      return render_template('base.html',user=user,previouspage="login")
    else:
      error = 'Invalid password'
    '''
    next = request.args.get('next')
    if not next_is_valide(next):
      return abort(401)
    return redirect(next or url_for('base'))
    '''
  return render_template('login.html',form=form,error=error)

@app.route('/logout')
def logout():
  logout_user()
  session['logged_in'] = False
  flash('You were logged out')
  return render_template('logout.html')



@app.route('/private', methods=['GET', 'POST'])
def private():
    this_route = url_for('.private')
    error = None
    if not session.get('logged_in'):
      abort(401)
    app.logger.info("Logging a test message from "+this_route)
    return render_template('private.html', error=error)




@app.route('/')
@app.route('/edinburgh/')
def edinburgh():
    return render_template('base.html'), 200


@app.route('/edinburgh/things-to-do/tours/')
def tours():
    return render_template('tours.html'), 200

@app.route('/edinburgh/things-to-do/attractions/')
def attractions():
    return render_template('attractions.html'), 200

@app.route('/edinburgh/things-to-do/attractions/edinburgh-castle')
def edinburghcastle():
    return render_template('edinburgh-castle.html'), 200

@app.route('/edinburgh/things-to-do/activities/')
def activities():
    return render_template('activities.html'), 200


@app.route('/edinburgh/accommodation/')
def accommodation():
  return render_template('accommodation.html'), 200

@app.route('/edinburgh/pubs/')
def pubs():
  return render_template('pubs.html'), 200


# Database pubs is not finished, No Time to continue
#
#def get_db():
#  db = getattr(g, 'db', None)
#  if db is None:
#    db = sqlite3.connect(db_location)
#    g.db = db
#  return db
#
#@app.teardown_appcontext
#def close_db_connection(exception):
#  db = getattr(g, 'db', None)
#  if db is not None:
#    db.close()
#
#def init_db():
#    with app.app_context():
#      db = get_db()
#      with app.open_resource('schema.sql', mode='r') as f:
#        db.cursor().executescript(f.read())
#      db.commit()
#
#
#@app.route('/edinburgh/pubs/')
#def pubs():
#    db = get_db()
#    db.cursor().execute('insert into pubs values ("Finnegans Wake", "Student Pub", "9B Victoria St", "6pm - 1am daily", "http://www.finnegans-wake.co.uk/")')
#    db.commit()
 # 
#
#
#    page = []
#    page.append('<html><ul>')
#    sql = "SELECT rowid, * FROM pubs ORDER BY pubtype"
#    for row in db.cursor().execute(sql):
#        page.append('<li>')
#        page.append(str(row))
#        page.append('</li>')
#
#    page.append('</ul><html>')
#    return ''.join(page)



@app.route('/contact/')
def contact():
    return render_template('contact.html'), 200

@app.route('/imprint/')
def imprint():
    return render_template('imprint.html'), 200

@app.route('/force404')
def force404():
    abort(404)

@app.errorhandler(404)
def page_not_found(error):
  return render_template('error404.html'), 404

@app.errorhandler(401)
def custom_401(error):
  return render_template('error401.html'), 404




if __name__ == "__main__":
    init(app)
    logs(app)
    app.run(
	debug=app.config['debug'],
        host=app.config['ip_address'],
        port=int(app.config['port']))
