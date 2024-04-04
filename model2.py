import replicate
from utils import *
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import re,json
from crawlbase import CrawlingAPI, ScraperAPI, LeadsAPI, ScreenshotsAPI, StorageAPI
from crawlbase import CrawlingAPI
import json
from flask import session
import datetime as DT;


def generate_text(prompt_input,system_prompt):
    print("prompt",prompt_input)
    output = replicate.run(
    "mistralai/mixtral-8x7b-instruct-v0.1",
    input={
        "top_k": 50,
        "top_p": 0.9,
        "prompt": system_prompt+f"<s>[INST] {prompt_input} [/INST] ",
        "temperature": 0.01,
        "max_new_tokens": 1024,

        "presence_penalty": 0,
        "frequency_penalty": 0
    }
)
    output ="".join(output)
    # print(output)

    return output


def get_math_answer(prompt_input):
    output = replicate.run(
    "mistralai/mixtral-8x7b-instruct-v0.1",
    input={
        "top_k": 50,
        "top_p": 0.9,
        "prompt": """<s>[INST] You are a brilliant math professor and your job is to understand the question and follow detailed steps and solve the answer to the problem provided to you. once you answer check back and evaluate if the answer is correct or not and then if needed recalculate it. once finished finally display the answer. If something is missing or needed request them back politely. [/INST]"""+f"""<s>[INST] {prompt_input} [/INST] """,
        "temperature": 0.7,
        "max_new_tokens": 1024,

        "presence_penalty": 0,
        "frequency_penalty": 0
    }
)
    output ="".join(output)
    # print(output)

    return output




def search_answer(question):
    api = CrawlingAPI({ 'token': 'rkcSMegJId6B-Wx6R9WNCw' })
    google_search_url = 'https://www.google.com/search?q='+question
    # options for Crawling API
    options = {
    'scraper': 'google-serp'
    }
    res=""
    try:
        response = api.get(google_search_url, options)
        if response['status_code'] == 200 and response['headers']['pc_status'] == '200':
            response_json = json.loads(response['body'].decode('latin1'))
            response_json=response_json["body"]["searchResults"]
            # print(response_json)
            full_results=""
            for i in range (min(len(response_json),4)):
                # print(response_json[i])
                full_results+=response_json[i]["description"] 

            system_prompt="You are a brilliant assistant and help in answering questions for the user."
            prompt_input=f"""Data:{full_results}
                            Based on the given data above can you answer {question}"""

            res= generate_text(prompt_input,system_prompt)
    except Exception as e:
        print("Exception",e)
        res="Sorry answer not found due to some internal error"
    return res








def instruction_format(sys_message: str):
    # note, don't "</s>" to the end
    return f'<s> [INST] {sys_message} [/INST]'

sys_msg = """You are a helpful AI assistant, you are an agent capable of using a variety of tools to answer a question. Here are a few of the tools available to you:

- Stocker: the Stocker should be used whenever you need to find information about a stock provided its symbol and a start date, you must understand the dates passed and convert them to a way that python code can understand.  It uses Python so make sure to write complete Python code required to perform the calculation required and make sure the Python returns your answer to the `output` variable.
- Search: the search tool should be used whenever you need to find information. It can be used to find information about everything
- Final Answer: the final answer tool must be used to respond to the user. You must use this when you have decided on an answer.
- InterestCalculator: the InterestCalculator should be used whenever you need to calculate interest for given capital, rate and period, and debit. if any of the values are missing from the question use None value as parameters so we dont get any error. It uses python so make sure to write the Python code required to perform the  calculation required and make sure the Python returns your answer to the `output` variable.
- RAG: The RAG is used whenever the user provided data along with the question and ask you answer about the question using above data. It uses Python so make sure to write complete Python code required to perform the calculation required and make sure the Python returns your answer to the `output` variable.  
- ProfileInfo: The PrfoileInfo should be used when you feel like user is asking questions that related to his info or to answer the question user info is needed then you have to use this tool. It uses Python so make sure to write complete Python code required to perform the calculation required and make sure the Python returns your answer to the `output` variable.
- Math: If user asks questions related to math provided some epressions or equations and any other math stuff except the calculate interest then you use this tool to answer 
If you think that particular tool can be used but are missing any information for a particular tool ask the missing information from the user and then use the tool. 
To use these tools you must always respond in JSON format containing `"toolname"` and `"input"` key-value pairs.
 For example, to answer the question, "What is the stock price of symbol CCL for since seven days?" you must use the Stocker tool like so:

```json
{
    "toolname": "Stocker",
    "input": "output=getstockdata(ticker='CCL', startdate=DT.date.today()+DT.timedelta(days=-7),enddate=None)"
}
```
or to answer a question like "What is the stock price of symbol CCL from jan 2023 to may 2023?" you must use the Stocker tool like so:
```json
{
    "toolname": "Stocker",
    "input": "output=getstockdata(ticker='CCL', startdate='2023-01-01',enddate='2023-05-31')"
}
```

or to answer "what is the interest for capital of 5000 euro for rate of 3%  for 4 years and debit in 2 years?"  you must use the InterestCalculator tool like so:

```json
{
    "toolname": "InterestCalculator",
    "input":"output=interest_compound(capital=5000,rate=3,period=4,debit=2)"
}
```

or to answer "What is my balance from last year?" you should use ProfileInfo tool like below:
```json
{
    "toolname":"ProfileInfo",
    "input":"What is my balance from last year?"

}


or to answer "Can you show me how much I have saved on a personal level over the last year so I can understand how much I can invest?" you should use ProfileInfo tool like below:
```json
{
    "toolname":"ProfileInfo",
    "input":"Can you show me how much I have saved on a personal level over the last year so I can understand how much I can invest?"

}



Or to answer the question "who is the current president of the USA?" you must respond:

```json
{
    "toolname": "Search",
    "input": "current president of USA"
}
```

Or to answer the question "evaluate x+3+2x when x is 1" you must respond:

```json
{
    "toolname": "Math",
    "input": "evaluate x+3+2x when x is 1"
}
```

Or to answer the question "x^2+x-2" you must respond:

```json
{
    "toolname": "Math",
    "input": "x^2+x-2"
}
```


Or to answer the question thats related to finance provided some data then you use this tool answer that question using the data
example provided "Money market funds invest in short-term debt securities and provide interest income with very low risk of changes in share value. Fund NAVs are typically set to one currency unit, but there have been instances over recent years in which the NAV of some funds declined when the securities they held dropped dramatically in value. Funds are differentiated by the types of money market securities they purchase and their average maturities.
Based on the given data above can you answer what is Money Market funds?" you must respond but remember if the data provided it not related to the question at all then you do not use this tool instead use "Search" tool:

```json
{
    "toolname": "RAG",
    "input": "Money market funds are investment vehicles that pool money from multiple investors to purchase short-term debt securities. These funds aim to offer investors a way to earn interest income while maintaining a very low risk of changes in the share value. The net asset value (NAV) of money market funds is typically set to one currency unit (e.g., $1 in the United States), providing an easy understanding of the share value for investors."

}
```

Remember if user question does not belong to any of the above or it is general question like greeting or welcome message chat and greet with him nicely and respond with strucutre below.

```json
{
    "toolname": "Answer",
    "input": "Nice to Meet you. How can I help you."

}
```

Let's get started. The users query is as follows.
"""


import json




def format_output(text: str):
    try:
        print(text)
        if "{" in text and "}" in text:
            resp=extract_json_from_string(text)
            if len(resp)>0:
                return resp
        
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
        return json.loads(full_json_str, strict=False)
    except Exception as e:
        print("json error", e)
        if "{" in text and "}" in text:
            resp=extract_json_from_string(text)
            if len(resp)>0:
                return resp
    return {}









from duckduckgo_search import DDGS

def use_tool(action: dict):
    # print(action)
    output=''
    toolname = action["toolname"]
    if toolname == "RAG":
        return {"rtype":"text","result":action["input"]}
    elif toolname=="InterestCalculator":
        local_vars = {}
        exec(action["input"], globals(), local_vars)
        return {"rtype":"text","result":f"Tool Interest: {local_vars['output']}"}
    elif toolname == "Stocker":
        fcall= get_stock_call(action["input"])
        local_vars = {}
        exec(fcall, globals(), local_vars)
        return {"rtype":"image","result":f"{local_vars['output']}"}
    elif toolname=="ProfileInfo":
        user_data= str(get_user_info(session['user_id']))
        prompt_input="""based on the data provided related to the user answer the user question
                         Data: """+user_data+f"Question: {action['input']}"
        system_prompt="You are a brilliant assistant and help in answering questions for the user."
        res= generate_text(prompt_input,system_prompt)
        return {"rtype":"text","result": res}
    elif toolname == "Search":
        res=search_answer(action["input"])
        return {"rtype":"text","result": res}
    elif toolname=='Math':
        res=get_math_answer(action["input"])
        return {"rtype":"text","result": res}
    else:
        # otherwise just assume final answer
        return {"rtype":"text","result":action["input"]}






def run(query: str,system_prompt):
    res = generate_text(query,system_prompt)
    # print(res)
    try:
        action_dict = format_output(res)
        response = use_tool(action_dict)
        return response
    except Exception as e:
        print("exception ",e)
        if '{' in str(res) and '}' in str(res) and 'rtype' in str(res):
            return res
        else:
            return {"rtype":"text","result":str(res)}

    # print(response)

    return response








def get_answer(query):
    system_prompt = instruction_format(sys_msg)
    output = run(query,system_prompt)
    # print(output)
    return output


# print(get_answer("capital of france?"))