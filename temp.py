from sympy import *
def interest_composite(income,rate,period,debit) :
    print("called")
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




from duckduckgo_search import DDGS

def use_tool(action: dict):
    print(action)
    output=''
    tool_name = action["tool_name"]
    if tool_name == "Final Answer":
        return "Assistant: "+action["input"]
    elif tool_name=="InterestCalculator":
        local_vars = {}
        exec(action["input"], globals(), local_vars)
        return f"Tool Interest: {local_vars['output']}"
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



action={'tool_name': 'Search', 'input': 'What is capital of paris'}
print(use_tool(action))

# import json 
# def format_output(text: str):
#     # print(text)
#     full_json_str = '{"tool_name": '+text

#     full_json_str= full_json_str.replace('\n', '').replace('\r', '').replace('\t', '')
#     full_json_str = full_json_str.strip()
#     if full_json_str.endswith("```"):
#         full_json_str = full_json_str[:-3]
#     return json.loads(full_json_str)



# a="""
# "RAG",
# "input":  "The beta of a portfolio is calculated by taking a weighted average of the betas of each individual security within the portfolio. The weights are determined by the proportion of each security's market value relative to the total market value of the portfolio.

# The Capital Asset Pricing Model (CAPM) is a financial model that describes the relationship between systematic risk and expected return for assets. According to the CAPM, the expected return of a security or a portfolio equals the rate on a risk-free security plus a risk premium. The risk premium is the market return in excess of the risk-free rate, multiplied by the asset's beta. Beta is a measure of the asset's sensitivity to market movements."
# }
# ```
# """


# print(format_output(a))