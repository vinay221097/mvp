from torch import bfloat16
import transformers
from utils import *

model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype=bfloat16,
    device_map='auto',
    cache_dir='/home/models'
)

tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

generate_text = transformers.pipeline(
    model=model, tokenizer=tokenizer,
    return_full_text=False,  # if using langchain set True
    task="text-generation",
    # we pass model parameters here too
    temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
    top_p=0.15,  # select from top tokens whose probability add up to 15%
    top_k=0,  # select from top 0 tokens (because zero, relies on top_p)
    max_new_tokens=512,  # max number of tokens to generate in the output
    repetition_penalty=1.1  # if output begins repeating increase
)


def instruction_format(sys_message: str, query: str):
    # note, don't "</s>" to the end
    return f'<s> [INST] {sys_message} [/INST]\nUser: {query}\nAssistant: ```json\n{{\n"tool_name": '

sys_msg = """You are a helpful AI assistant, you are an agent capable of using a variety of tools to answer a question. Here are a few of the tools available to you:

- Calculator: the calculator should be used whenever you need to perform a calculation, no matter how simple. It uses Python so make sure to write complete Python code required to perform the calculation required and make sure the Python returns your answer to the `output` variable.
- Search: the search tool should be used whenever you need to find information. It can be used to find information about everything
- Final Answer: the final answer tool must be used to respond to the user. You must use this when you have decided on an answer.
- InterestCalculator: the InterestCalculator should be used whenever you need to calculate interest for given capital, rate and period, and debit. It uses python so make sure to write the Python code required to perform the  calculation required and make sure the Python returns your answer to the `output` variable.
- RAG: The RAG is used whenever the user provided data along with the question and ask you answer about the question using above data.  
If you think that particular tool can be used but are missing any information for a particular tool ask the missing information from the user and then use the tool. 
To use these tools you must always respond in JSON format containing `"tool_name"` and `"input"` key-value pairs. For example, to answer the question, "what is the square root of 51?" you must use the calculator tool like so:

```json
{
    "tool_name": "Calculator",
    "input": "from math import sqrt; output = sqrt(51)"
}
```
or to answer "what is the interest for capital of 5000 euro for rate of 3%  for 4 years and debit in 2 years?"  you must use the InterestCalculator tool like so:

```json
{
    "tool_name": "InterestCalculator",
    "input":"output=interest_composite(5000,3,4,2)"
}
```

Or to answer the question "who is the current president of the USA?" you must respond:

```json
{
    "tool_name": "Search",
    "input": "current president of USA"
}
```

Or to answer the question "Money market funds invest in short-term debt securities and provide interest income with very low risk of changes in share value. Fund NAVs are typically set to one currency unit, but there have been instances over recent years in which the NAV of some funds declined when the securities they held dropped dramatically in value. Funds are differentiated by the types of money market securities they purchase and their average maturities.
Based on the given data above can you answer what is Money Market funds?" you must respond:

```json
{
    "tool_name": "RAG",
    "input": "Money market funds are investment vehicles that pool money from multiple investors to purchase short-term debt securities. These funds aim to offer investors a way to earn interest income while maintaining a very low risk of changes in the share value. The net asset value (NAV) of money market funds is typically set to one currency unit (e.g., $1 in the United States), providing an easy understanding of the share value for investors."

}
```

Remember, even when answering to the user, you must still use this JSON format! If you'd like to ask how the user is doing you must write:

```json
{
    "tool_name": "Final Answer",
    "input": "How are you today?"
}
```

Let's get started. The users query is as follows.
"""

from sympy import *

def interest_composite(income,rate,period,debit) :
    #x = symbols("x")
    eq=0
    try:
        c,r = symbols("c,r", real=True)
        n,d = symbols("n,d", integer=True)
        n=period
        c=income
        r=rate
        d=debit 
        if debit==0:
            eq=c*(1+r*(n-d)/100)
        else:
            eq=d*c/(n)*(1+r*(n-d)/100)
    except Exception as e:
        print(e)
    return eq



import json

def format_output(text: str):
    full_json_str = '{\n"tool_name": '+text
    full_json_str = full_json_str.strip()
    if full_json_str.endswith("```"):
        full_json_str = full_json_str[:-3]
    return json.loads(full_json_str)


from duckduckgo_search import DDGS

def use_tool(action: dict):
    print(action)
    output=''
    tool_name = action["tool_name"]
    if tool_name == "Final Answer":
        return "Assistant: "+action["input"]
    elif tool_name=="InterestCalculator":
        exec(action["input"])
        return f"Tool Interest: {output}"
    elif tool_name == "Calculator":
        exec(action["input"])
        return f"Tool Output: {output}"
    elif tool_name == "Search":
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
        return f"Tool Output: {info}"
    else:
        # otherwise just assume final answer
        return action["input"]





def run(query: str):
    res = generate_text(query)
    action_dict = format_output(res[0]["generated_text"])
    response = use_tool(action_dict)
    # print(response)
    full_text = f"{query}{res[0]['generated_text']}\n{response}"
    return response, full_text









def get_answer(query):
    input_prompt = instruction_format(sys_msg, query)
    output,full_text = run(input_prompt)
    # print(output)
    return output