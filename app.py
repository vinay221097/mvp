import datetime, os, logging
import jinja2, sys, time
from flask import Flask, Response, render_template, request,session,redirect,url_for
from html import escape
from werkzeug.security import check_password_hash
from flask_minify import Minify
import pandas as pd
from datetime import date

app = Flask(__name__,static_url_path='/static', 
            static_folder='static',
            template_folder='templates')

# random string
app.secret_key = "af95d160b65aac2494ce48226202559d1f82563"

Minify(app=app, html=True, js=False, cssless=False)

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# template_dir = os.path.abspath('../templates')
# app = Flask(__name__,template_folder=template_dir)

my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['/home'
    ]),
])
app.jinja_loader = my_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
env_file = find_dotenv(f'.env.{os.getenv("FLASK_ENV", "development")}')

load_dotenv(env_file)
uri = os.getenv('DATABASE_URI')
DB=os.getenv('DB')
USERSDB=os.getenv('USERSDB')
# Create a new client and connect to the server
client = MongoClient(uri, maxPoolSize=70)
db = client[DB]  # Replace with your database name
collection = db[USERSDB]  # Replace with your collection name


def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get("loggedin") or request.endpoint=='validate' or request.endpoint=='detailsconfirm':
            return f(*args, **kwargs)
        else:
            return redirect("login")
    return decorated_func




@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=''
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        # Create variables for easy access
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        # Retrieve the hashed password
        db = client[DB]
        users = db[USERSDB]
        user = users.find_one({'username': username})
        if user:
            if check_password_hash(user['password'],password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['username'] = user['username']
                # Redirect to home page

                return redirect(url_for('hello'))
            else:
                msg = 'Email o Password errate'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Email o Password errate'
        

    return render_template('home/login.html', msg=msg)




@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))





@app.route('/')
def hello():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    return render_template("home/index.html", machine_df=df)


@app.route('/static')
def static_file(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    # Set DEBUG=True to enable
    app.run(debug=debug)