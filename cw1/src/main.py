import ConfigParser
import logging

from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, g, redirect, render_template, flash, url_for, abort

app = Flask(__name__)


@app.route('/private', methods=['GET', 'POST'])
def private():
    this_route = url_for('.private')
    error = None
    if not session.get('logged_in'):
      abort(401)
    app.logger.info("Logging a test message from "+this_route)
    return render_template('private.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    this_route = url_for('.login')
    error = None
    if request.method == 'POST':
      if request.form['username'] != app.config['username']:
        error = 'Invalid username'
      elif request.form['password'] != app.config['password']:
        error = 'Invalid password'
      else:
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('private'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return render_template('logout.html')

@app.route('/config/')
def config():
  str = []
  str.append('Debug: '+app.config['DEBUG'])
  str.append('port: '+app.config['port'])
  str.append('url: '+app.config['url'])
  str.append('ip_address: '+app.config['ip_address'])
  str.append('username: '+app.config['username'])
  return '\t'.join(str)

def init(app):
    config = ConfigParser.ConfigParser()
    config_location = "etc/config.cfg"
    try:
        config.read(config_location)

        app.config['DEBUG'] = config.get("config", "debug")
        app.config['ip_address'] = config.get("config", "ip_address")
        app.config['port'] = config.get("config", "port")
        app.config['url'] = config.get("config", "url")
        app.secret_key = config.get("config", "secret_key")
        app.config['username'] = config.get("config", "username")
        app.config['password'] = config.get("config", "password")

        app.config['log_file'] = config.get("logging", "name")
        app.config['log_location'] = config.get("logging", "location")
        app.config['log_level'] = config.get("logging", "level")
    except:
        print ("Could not read configs from: "), config_location

def logs(app):
    log_pathname = app.config['log_location'] + app.config['log_file']
    file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10, backupCount=1024)
    file_handler.setLevel(app.config['log_level'])
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.setLevel(app.config['log_level'])
    app.logger.addHandler(file_handler)




@app.route('/')
def root():
  return render_template('base.html'), 200


@app.route('/castles/')
def castles():
    return render_template('castle.html'), 200

@app.route('/castles/blair/')
def blair():
    return render_template('blair.html'), 200

@app.route('/castles/caerlaverock/')
def caerlaverock():
   return render_template('caerlaverock.html'), 200

@app.route('/castles/culzean/')
def culzean():
    return render_template('culzean.html'), 200

@app.route('/castles/dunvegan/')
def dunvegan():
    return render_template('dunvegan.html'), 200

@app.route('/castles/edinburgh/')
def edinburgh():
    return render_template('edinburgh.html'), 200

@app.route('/castles/eileandonan/')
def eileandonan():
    return render_template('eileandonan.html'), 200

@app.route('/castles/fyvie/')
def fyvie():
    return render_template('fyvie.html'), 200

@app.route('/castles/glamis/')
def glamis():
    return render_template('glamis.html'), 200

@app.route('/castles/stirling/')
def stirling():
    return render_template('stirling.html'), 200


@app.route('/contact/upload/userpicture/')
def userpicture():
  this_route = url_for('.userpicture')
  return render_template('userpictures.html'), 200

@app.route("/contact/upload/", methods=['POST', 'GET'])
def upload():
  if request.method == 'POST':
    f = request.files['datafile']
    f.save('static/uploads/userpicture1.png')
    return redirect(url_for('userpicture'))
  else:
    page='''
    <html>
    <body>
    <p>Here you can upload your picture</p>
    <form action="" method="post" name="form" enctype="multipart/form-data">
      <input type="file" name="datafile" />
      <input type="submit" name="submit" id="submit"/>
    </form>
    </body>
    </html>
    '''
    return page, 200

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
        host = app.config['ip_address'],
        port = int(app.config['port']))
