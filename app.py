import datetime, os, logging
import jinja2, sys, time
from flask import Flask, Response, render_template, request,session,redirect,url_for,jsonify
from html import escape
from werkzeug.security import check_password_hash,generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_minify import Minify
import pandas as pd
import hashlib
from datetime import date
from utils import *
from chat import *
import sqlite3
app = Flask(__name__,static_url_path='/static', 
            static_folder='static',
            template_folder='templates')

# random string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
# env_file = find_dotenv(f'.env.{os.getenv("FLASK_ENV", "development")}')




# db = SQLAlchemy(app)
con = sqlite3.connect("users.db")




@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM user WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            msg = "Username already exists. Please choose a different one."
        else:
            # Hash the password before storing it
            hashed_password = generate_password_hash(password)

            # Insert the new user into the database
            cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()

            return "User registered successfully. <a href='/login'>Login</a>"
    
    return render_template('home/register.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Retrieve the user by username
        cursor.execute("SELECT * FROM user WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            conn.close()
            return redirect(url_for("hello"))
        else:
            msg = "Invalid username or password."
            conn.close()

    return render_template('home/login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))







chatgpt_output = 'Chat log: /n'

cwd = os.getcwd()
i = 1
# Define the name of the bot
name = 'Finn'

# Define the role of the bot
role = 'Assistant'



@app.route("/get")
def get_bot_response():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    userText = request.args.get('msg')
    response_content = chat(userText)
    return jsonify(response_content)




# Initialize chat history
chat_history = ''



# Function to handle user chat input
def chat(user_input):
    chatgpt_raw_output = get_answer_with_ai_public(user_input)
    return chatgpt_raw_output




# Function to get a response from the chatbot
def get_response(userText):
    return chat(userText)











@app.route('/')
def hello():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template("home/chat.html")


@app.route('/static')
def static_file(path):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return app.send_static_file(path)


if __name__ == "__main__":
    # Set DEBUG=True to enable
    app.run(debug=debug)