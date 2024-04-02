import json


def format_output(text: str):
    try:
        # print(text)
        if type(text)!= str:
            text=str(text)
        full_json_str= text.replace('\n', '').replace('\r', '').replace('\t', '').replace("  "," ")
        if 'toolname' not in text:
            full_json_str = '{"toolname": '+text


        full_json_str = full_json_str.strip()
        # print(full_json_str)
        if "```json" in full_json_str:
            full_json_str=full_json_str.split("```json")[1]
            # print(full_json_str)
        if "```" in full_json_str:
            full_json_str=full_json_str.split("```")[0]
            # print(full_json_str)


        # print(full_json_str)
        if full_json_str.endswith("```"):
            full_json_str = full_json_str[:-3]
        return json.loads(full_json_str)
    except Exception as e:
        print("json error", e)
        if "{" in text and "}" in text:
            resp=extract_json_from_string(text)
            if len(resp)>0:
                return resp
    return {}


text="""
Of course, to answer your question, I will use the Stocker tool to get the stock data for the BAMI.MI share over the last year and then use a Python library to graph the trend. Here is the JSON response: ```json { "toolname": "Stocker", "input": "import datetime as DT; import matplotlib.pyplot as plt; import pandas as pd;\noutput=get_stock_data(ticker='BAMI. MI', start_date=DT.date.today()+DT.timedelta(days =-365),end_date='2023-12-18')\nplt.figure(figsize=(12,5));plt.plot(output['Date' ], output['Close']);plt.title('BAMI.MI Stock price performance over the last year');plt.xlabel('Data');plt.ylabel('Price');plt. grid();plt.show()" } ``` This code will retrieve the last year's stock data and graph the closing price action. Note that the "get_stock_data" function returns a DataFrame containing the stock data and we extract the "Date" and "Close" columns to plot the chart. The `plt.figure`, `plt.plot`, `plt.title`, `plt.xlabel`, `plt.ylabel`, `plt.grid` and `plt.show` functions are used to customize and display the plot.
"""

input_string=str(format_output(text))

# input_string = "import datetime as DT; import matplotlib.pyplot as plt; import pandas as pd;output=get_stock_data(ticker='BAMI. MI', start_date=DT.date.today()+DT.timedelta(days =-365),end_date=None)plt.figure(figsize=(12,5));plt.plot(output['Date' ], output['Close']);plt.title('BAMI.MI Stock price performance over the last year');plt.xlabel('Data');plt.ylabel('Price');plt. grid();plt.show()"

# Find the start index of 'get_stock_data'
start_index = input_string.find('get_stock_data')

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
    print(specific_call)
else:
    print("Function call not found.")


