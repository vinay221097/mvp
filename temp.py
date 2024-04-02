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


input_string=str(format_output(text))

# input_string = "import datetime as DT; import matplotlib.pyplot as plt; import pandas as pd;output=get_stock_data(ticker='BAMI. MI', start_date=DT.date.today()+DT.timedelta(days =-365),end_date=None)plt.figure(figsize=(12,5));plt.plot(output['Date' ], output['Close']);plt.title('BAMI.MI Stock price performance over the last year');plt.xlabel('Data');plt.ylabel('Price');plt. grid();plt.show()"




