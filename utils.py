from sympy import *
import yfinance as yf
import dateparser
import pandas as pd
import io
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg')

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





def parse_date(date_str):
    """Parse any date string into a datetime object."""
    return dateparser.parse(str(date_str))

def get_stock_data(ticker, start_date, end_date=None):
    """
    Fetch and display stock data for a given ticker and date range.
    
    Parameters:
    - ticker: Stock ticker symbol as a string.
    - start_date: Start date in various formats.
    - end_date: End date in various formats. If None, current date is used.
    """
    # Parse the start and end dates
    start = parse_date(start_date)
    if end_date:
        end = parse_date(end_date)
    else:
        end = pd.Timestamp.today()  # Use current date if end date is not provided
    
    # Fetch the stock data
    stock_data = yf.download(ticker, start=start, end=end)
    
    # Display the data
    buf = io.BytesIO()
    plt.figure(figsize=(10, 6))
    stock_data['Close'].plot(title=f'{ticker} Stock Closing Prices')
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Encode the image to base64 string
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Return the base64 string
    return image_base64




