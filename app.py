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
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64


app = Flask(__name__,static_url_path='/static', 
            static_folder='static',
            template_folder='templates')

# random string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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





def get_user_info(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor = conn.execute('SELECT * FROM user_info WHERE email = ?', (email,))
    row = cursor.fetchone()
    if row:
        # Extract column names from the cursor description
        columns = [column[0] for column in cursor.description]
        # Create a dictionary where keys are column names and values are row values
        user_info_dict = dict(zip(columns, row))
    else:
        user_info_dict = {}

    conn.close()
    return user_info_dict


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
            session['user_id'] = user[1]
            conn.close()
            return redirect(url_for("hello"))
        else:
            msg = "Invalid username or password."
            conn.close()

    return render_template('home/login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('hello'))



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Sample email to work with, in real scenario pass it dynamically or ensure authentication
    user_email = session['user_id']
    user_info = get_user_info(user_email)

    if request.method == 'POST':
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_info SET
            name = ?,
            surname = ?,
            date_of_birth = ?,
            province_of_birth = ?,
            place_of_birth = ?,
            gender = ?,
            citizenship = ?,
            conjugated = ?,
            number_of_children = ?,
            number_of_dependent_children = ?,
            annual_income = ?,
            total_liquidity = ?,
            invested_asset_value = ?,
            value_of_real_estate = ?,
            vehicle_value = ?,
            total_debt_values = ?
            WHERE email = ?''', (
            request.form['name'],
            request.form['surname'],
            DT.datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
            request.form['province_of_birth'],
            request.form['place_of_birth'],
            request.form['gender'],
            request.form.get('citizenship', 'No'),
            request.form['conjugated'],
            request.form['number_of_children'],
            request.form['number_of_dependent_children'],
            request.form['annual_income'],
            request.form['total_liquidity'],
            request.form['invested_asset_value'],
            request.form['value_of_real_estate'],
            request.form['vehicle_value'],
            request.form['total_debt_values'],
            user_email
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('profile'))

    return render_template('home/profile.html', user_info=user_info)



chatgpt_output = 'Chat log: /n'

cwd = os.getcwd()
i = 1
# Define the name of the bot
name = 'Finn'

# Define the role of the bot
role = 'Assistant'


def hardcode(message):
    if "it0005518128" in message:
        return """Riusciresti a dirmi qual è il tuo prezzo medio di carico? In caso negativo. il titolo nella giornata di ieri, 28 marzo 2024, ha chiuso ad un prezzo di 106,05€, questo significa che se l’avessi comprato al prezzo minimo del 5 ottobre 2023, pari a 96,85€ il capital gain alla chiusura di ieri sarebbe del 9,912%, mentre se fosse al prezzo massimo pari a 97,45€ massimo il capital gain sarebbe del 9,236%. 
                Inoltre, per calcolare il tuo guadagno è necessario tenere in considerazione anche il rateo maturato dalla data di acquisto, pari a 180 giorni al tasso di interesse dell’obbligazione pari a 4,40%.
                Per calcolare con esattezza il tuo guadagno riusciresti a dirmi il prezzo medio di carico che quantità hai acquisito? """
    elif "carico" in message:
        return "Ad un prezzo medio di carico di 97€, il capital gain teorico è pari a 9,742%, mentre il rateo maturato è pari a 297,21€."
    elif "risparmi" in message:
        return "Analizzando il tuo profilo di rischio e i tuoi obiettivi, ed ipotizzando un risparmio per l’anno futuro in linea con quello passato e pari a 5mila euro, allora ti suggerirei di investire in un piano di accumulo con un orizzonte temporale di 5-7 anni, in modo da sfruttare il cost average, investendo inizialmente una cifra di 2000€ e versando mensilmente circa 200 euro. La restante parte del risparmio in obbligazioni a basso rischio e legate all’inflazione con un orizzonte più breve pari a 1-3 anni."
    elif "spese" in message:
        return "spese"
    else:
        return None




@app.route("/get")
def get_bot_response():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    userText = request.args.get('msg')

    test= hardcode(userText)
    if test !=None and test!="spese":
        res={"rtype":"text","result":test}
        return jsonify(res)
    elif test !=None and test=="spese":
        return jsonify(plotter())

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






def process_excel(file_path):
    df = pd.read_excel(file_path)  # Assuming the file is an Excel file
    # Convert 'Data' column to datetime format
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')

    # Extract month and year from the 'Data' column
    df['Month'] = df['Data'].dt.month
    df['Year'] = df['Data'].dt.year

    # Define categories of expenses
    categories = ['Utenze', 'Alimentari', 'Trasporti', 'Hotel Ristoranti e Viaggi', 'Giochi Cultura e Spettacoli', 'Mutui, finanziamenti e assicurazioni', 'Altre spese']

    # Create a pivot table for each category spending in each month
    pivot_table = df.pivot_table(index='Moneymap', columns=['Year', 'Month'], values='Movimento', aggfunc='sum', fill_value=0)

    # Filter the pivot table for categories of interest
    category_pivot = pivot_table.loc[categories]

    # Calculate the difference from the previous month
    category_diff = category_pivot.diff(axis=1)
    
    # Process analysis results
    total_non_essential_spending = 15192
    total_spending = 115488
    percentage_non_essential = 13.15
    most_spending_category_overall = 'Mutui, finanziamenti e assicurazioni'
    total_spending_overall = 8841
    most_spending_category_each_month = {
        'Hotel Ristoranti e Viaggi': '(2023, 5)',
        'Giochi Cultura e Spettacoli': '(2024, 2)',
        'Mutui, finanziamenti e assicurazioni': '(2023, 12)',
        'Altre spese': '(2023, 7)'
    }
    total_spending_each_month = {
        'Hotel Ristoranti e Viaggi': 647,
        'Giochi Cultura e Spettacoli': 78,
        'Mutui, finanziamenti e assicurazioni': 1066,
        'Altre spese': 2285
    }

    return category_diff, total_non_essential_spending, total_spending, percentage_non_essential, most_spending_category_overall, total_spending_overall, most_spending_category_each_month, total_spending_each_month

def generate_plot(category_diff):
    plt.figure(figsize=(12, 6))
    for category in category_diff.index:
        x_values = [str(col) for col in category_diff.columns]
        y_values = category_diff.loc[category].astype(float)
        plt.plot(x_values, y_values, marker='o', label=category)

    plt.title('Differenze di spesa rispetto al mese precedente per ciascuna categoria')
    plt.xlabel('Month')
    plt.ylabel('Difference in Spending')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Convert plot to bytes object and then to base64 for embedding in HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return plot_data




def plotter():
    files=os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter out only .xlsx files
    xlsx_files = [file for file in files if file.endswith('.xlsx')]
    file_path= xlsx_files[0]
    df = pd.read_excel(file_path)  # Assuming the file is an Excel file
    # Convert 'Data' column to datetime format
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')

    # Extract month and year from the 'Data' column
    df['Month'] = df['Data'].dt.month
    df['Year'] = df['Data'].dt.year

    # Define categories of expenses
    categories = ['Utenze', 'Alimentari', 'Trasporti', 'Hotel Ristoranti e Viaggi', 'Giochi Cultura e Spettacoli', 'Mutui, finanziamenti e assicurazioni', 'Altre spese']

    # Create a pivot table for each category spending in each month
    pivot_table = df.pivot_table(index='Moneymap', columns=['Year', 'Month'], values='Movimento', aggfunc='sum', fill_value=0)

    # Filter the pivot table for categories of interest
    category_pivot = pivot_table.loc[categories]

    # Calculate the difference from the previous month
    category_diff = category_pivot.diff(axis=1)
    res=generate_plot(category_diff)
    rjson= {"rtype":"image","result":res}
    return rjson





@app.route('/uploadstatement', methods=['GET'])
def uploadstatement():
    return render_template('home/uploadstatement.html')


@app.route('/results', methods=['GET','POST'])
def results():
    files=os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter out only .xlsx files
    xlsx_files = [file for file in files if file.endswith('.xlsx')]
    file_path= xlsx_files[0]
    if request.method=='POST':
        if 'file' not in request.files:
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            return redirect('/')
        if file:
            file_path = app.config['UPLOAD_FOLDER'] + file.filename
            file.save(file_path)

    category_diff, total_non_essential_spending, total_spending, percentage_non_essential, most_spending_category_overall, total_spending_overall, most_spending_category_each_month, total_spending_each_month = process_excel(file_path)
    plot = generate_plot(category_diff)
    money_map_categories = category_diff.index.tolist()  # Extract category list
    return render_template('home/dashboard.html', plot=plot, money_map_categories=money_map_categories, category_diff=category_diff.to_dict(),
                           total_non_essential_spending=total_non_essential_spending, total_spending=total_spending,
                           percentage_non_essential=percentage_non_essential, most_spending_category_overall=most_spending_category_overall,
                           total_spending_overall=total_spending_overall, most_spending_category_each_month=most_spending_category_each_month,
                           total_spending_each_month=total_spending_each_month)
    






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