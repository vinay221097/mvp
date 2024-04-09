from serpapi import GoogleSearch
import json
import re
from sympy import symbols, sympify
from math import *
from sympy import Symbol,Eq,solve
import re
def find_solutions_1(expression):
    try:
        # Sostituisci "^" con "**" per gestire la notazione esponenziale
        expression = re.sub(r'(?<=[0-9a-zA-Z])\^', '**', expression)

        # Sostituisci la notazione del coefficiente
        expression = re.sub(r'([0-9a-zA-Z])x', r'\1*x', expression)

        # Divide l'espressione in due parti: lato sinistro e lato destro dell'uguale "="
        sides = expression.split("=")
        left_side = sides[0]
        right_side = sides[1] if len(sides) > 1 else '0'
        
        # Definisci il simbolo e analizza le due parti dell'equazione
        x = Symbol('x')
        left_expression = sympify(left_side)
        right_expression = sympify(right_side)

        # Definisci l'equazione come uguaglianza tra le due parti
        equation = left_expression - right_expression

        solutions = solve(equation, x)
        numeric_solutions = [solution.evalf() for solution in solutions]
        print(numeric_solutions)
        return numeric_solutions
    except Exception as e:
        print("Si è verificato un errore:", e)
        return None


question="valuta x^2-2x+1=0"

print(find_solutions_1(question))