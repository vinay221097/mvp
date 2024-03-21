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



action={'tool_name': 'InterestCalculator', 'input': 'output=interest_composite(100,8,5,2)'}
print(use_tool(action))

