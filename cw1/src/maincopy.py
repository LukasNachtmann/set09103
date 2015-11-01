from flask import Flask, render_template, redirect, request, url_for, abort
app = Flask(__name__)

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


@app.route('/castles/userpictures/')
def userpictures():
  return render_template('userpictures.html'), 200

@app.route("/castles/upload/", methods=['POST', 'GET'])
def upload():
  if request.method == 'POST':
    f = request.files['datafile']
    f.save('static/uploads/file1.png')
    return "Picture uploaded"
  else:
    page='''
    <html>
    <body>
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

@app.route('/private/')
def private():
    return redirect(url_for('login'))

@app.route('/login/')
def login():
    return render_template('login.html'), 200

@app.route('/force404')
def force404():
    abort(404)

@app.errorhandler(404)
def page_not_found(error):
  return render_template('error404.html'), 404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
