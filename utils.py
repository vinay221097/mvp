from sympy import *
import yfinance as yf
import dateparser
import pandas as pd

import io
import matplotlib.pyplot as plt
import base64
import matplotlib
import re
import json
import datetime as DT;
import sqlite3
matplotlib.use('Agg')



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
    print(user_info_dict)
    return user_info_dict




def interest_compound(capital=None,rate=None,period=None,debit=None) :
    if capital is None:
        return "Per calcolare il tasso di interesse è necessario inserire il capitale: "
    if rate is None:
        return "Il calcolo dell'interesse di basa su un tasso %, per favore digitalo per procedere col calcolo: "
    if period is None:
        return "Il calcolo dell'interesse dipende dalla durata del debito, digitalo per favore: "
    if debit is None:
        debit=0
    #x = symbols("x")
    try:
        c,r = symbols("c,r", real=True)
        n,d = symbols("n,d", integer=True)
        n=period
        c=capital
        r=rate
        d=debit
        eq=0
        if debit==0:
          eq=c*(1+r*(n-d)/100) -c
        else:
          eq=d*c/(n)*(1+r*(n-d)/100) -c
    except Exception as e:
        print(e)
    return eq




def extract_json_from_string(text):
    regex = r"\{(?:[^{}]|(?:\"(?:\\.|[^\"\\])*\")|\{(?:[^{}]|(?:\"(?:\\.|[^\"\\])*\"))*\})*\}"
    matches = re.findall(regex, text)
    output = {}
    if len(matches) > 0:
        temp = matches[0]
        if type(temp) == str:
            output = json.loads(temp)
        elif type(temp) == dict:
            output = temp
    return output


def parse_date(date_str):
    """Parse any date string into a datetime object."""
    return dateparser.parse(str(date_str))

def getstockdata(ticker, startdate, enddate=None):
    """
    Fetch and display stock data for a given ticker and date range.
    
    Parameters:
    - ticker: Stock ticker symbol as a string.
    - start_date: Start date in various formats.
    - end_date: End date in various formats. If None, current date is used.
    """
    # Parse the start and end dates
    start = parse_date(startdate)
    if enddate:
        end = parse_date(enddate)
    else:
        end = pd.Timestamp.today()  # Use current date if end date is not provided
    
    # Fetch the stock data
    stock_data = yf.download(ticker, start=start, end=end)
    
    # Display the data
    buf = io.BytesIO()
    plt.figure(figsize=(10, 6))
    stock_data['Close'].plot(title=f'{ticker} Stock Closing Prices')
    plt.xlabel('Date')
    plt.ylabel('Close Price ')
    # plt.show()
    plt.savefig(buf, format='png')
    
    plt.close()
    buf.seek(0)
    
    # Encode the image to base64 string
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Return the base64 string
    return image_base64



def get_stock_call(input_string:str):
    # Find the start index of 'get_stock_data'
    start_index = input_string.find('getstockdata')

    # Ensure 'get_stock_data' is in the string
    if start_index != -1:
        # Find the index of the opening parenthesis of the 'get_stock_data' function call
        start_parenthesis_index = input_string.find('(', start_index)
        
        # Start counting from the first opening parenthesis
        open_parentheses_count = 1  # Start with 1 to account for the first opening parenthesis
        end_index = start_parenthesis_index + 1
        
        # Iterate over the string starting after the '(' of 'get_stock_data'
        while end_index < len(input_string) and open_parentheses_count > 0:
            if input_string[end_index] == '(':
                open_parentheses_count += 1
            elif input_string[end_index] == ')':
                open_parentheses_count -= 1
            end_index += 1
        
        # The end_index will be one past the closing ')' of the function call, so we don't need to adjust it
        
        # Extract the complete function call
        specific_call = input_string[start_index:end_index]
        return f"output={specific_call}"
    else:
        return input_string