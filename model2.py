import replicate
from utils import *

def generate_text(prompt_input,system_prompt):
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
    print(output)

    return output


def instruction_format(sys_message: str):
    # note, don't "</s>" to the end
    return f'<s> [INST] {sys_message} [/INST]'

sys_msg = """You are a helpful AI assistant, you are an agent capable of using a variety of tools to answer a question. Here are a few of the tools available to you:

- Stocker: the Stocker should be used whenever you need to find information about a stock provided its symbol and a start date, you must understand the dates passed and convert them to a way that python code can understand.  It uses Python so make sure to write complete Python code required to perform the calculation required and make sure the Python returns your answer to the `output` variable.
- Search: the search tool should be used whenever you need to find information. It can be used to find information about everything
- Final Answer: the final answer tool must be used to respond to the user. You must use this when you have decided on an answer.
- InterestCalculator: the InterestCalculator should be used whenever you need to calculate interest for given capital, rate and period, and debit. if any of the values are missing from the question use None value as parameters so we dont get any error. It uses python so make sure to write the Python code required to perform the  calculation required and make sure the Python returns your answer to the `output` variable.
- RAG: The RAG is used whenever the user provided data along with the question and ask you answer about the question using above data.  
-
If you think that particular tool can be used but are missing any information for a particular tool ask the missing information from the user and then use the tool. 
To use these tools you must always respond in JSON format containing `"toolname"` and `"input"` key-value pairs.
 For example, to answer the question, "What is the stock price of symbol CCL for since seven days?" you must use the Stocker tool like so:

```json
{
    "toolname": "Stocker",
    "input": "import datetime as DT;output=get_stock_data(ticker='CCL', start_date=DT.date.today()+DT.timedelta(days=-7),end_date=None)"
}
```
or to answer a question like "What is the stock price of symbol CCL from jan 2023 to may 2023?" you must use the Stocker tool like so:
```json
{
    "toolname": "Stocker",
    "input": "import datetime as DT;output=get_stock_data(ticker='CCL', start_date='2023-01-01',end_date='2023-05-31')"
}
```

or to answer "what is the interest for capital of 5000 euro for rate of 3%  for 4 years and debit in 2 years?"  you must use the InterestCalculator tool like so:

```json
{
    "toolname": "InterestCalculator",
    "input":"output=interest_compound(capital=5000,rate=3,period=4,debit=2)"
}
```

Or to answer the question "who is the current president of the USA?" you must respond:

```json
{
    "toolname": "Search",
    "input": "current president of USA"
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


Let's get started. The users query is as follows.
"""

from sympy import *

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



import json

def format_output(text: str):
    # print(text)
    if type(text)!= str:
        text=str(text)
    full_json_str= text.replace('\n', '').replace('\r', '').replace('\t', '').replace("  "," ")
    if 'toolname' not in text:
        full_json_str = '{"toolname": '+text


    full_json_str = full_json_str.strip()
    print(full_json_str)
    if "```json" in full_json_str:
        full_json_str=full_json_str.split("```json")[1]
        print(full_json_str)
    if "```" in full_json_str:
        full_json_str=full_json_str.split("```")[0]
        print(full_json_str)


    # print(full_json_str)
    if full_json_str.endswith("```"):
        full_json_str = full_json_str[:-3]
    return json.loads(full_json_str)


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
        local_vars = {}
        exec(action["input"], globals(), local_vars)
        return {"rtype":"image","result":f"{local_vars['output']}"}
    elif toolname == "Search":
        contexts = []
        with DDGS() as ddgs:
            results = ddgs.text(
                action["input"],
                region="wt-wt", safesearch="on",
                max_results=3
            )
            for r in results:
                contexts.append(r['body'])
        info = "\n---\n".join(contexts)        
        return {"rtype":"text","result":f"Tool Output: {info}"}
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