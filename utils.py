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
