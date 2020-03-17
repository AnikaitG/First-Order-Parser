import sys
import string
import networkx as nx
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt

def updateLog(status=0, errmsg=''):
    with open("log.txt", "w") as log_file:
        if status == 1:
            log_file.write("Error in input file: " + errmsg)
            sys.exit()
        elif status == 2:
            log_file.write("Correct format in input file. Grammar given in 'grammar.txt'\nInvalid formula: " + errmsg)
            sys.exit()
        else:
            log_file.write("Correct format in input file. Grammar given in 'grammar.txt'\nFormula is valid. Abstract syntax tree given in 'tree.png'")

def getInput():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Please enter the name of the input file: ")
    try:
        input_file = open(filename, 'r')
    except FileNotFoundError:
        updateLog(1, "Requested file not found")
    input_text = input_file.readlines()
    prev_set = ""
    for line in input_text:
        wordlist = line.split()
        set_name = wordlist[0]
        if set_name[-1] != ':':
            if prev_set == "":
                updateLog(1,"Input file must begin with set name")
            set_name = prev_set
            i = 0
        else:
            set_name = set_name[:-1]
            i = 1
        if set_name not in sets:
            updateLog(1,"Invalid set name " + set_name)
        prev_set = set_name
        for word in wordlist[i:]:
            sets[set_name].append(word)
    input_file.close()

def setPredicates():
    p = {}
    for predicate in sets["predicates"]:
        arity = predicate.partition('[')[2][:-1]
        try:
            if int(arity) <= 0:
                updateLog(1, "Invalid arity " + arity + ", arity must be a positive integer")
        except ValueError:
            updateLog(1, "Invalid arity " + arity + ", arity must be a positive integer")
        predicate = predicate.partition('[')[0]
        p[predicate] = int(arity)
    return p

def setProductions():
    productions = {}
    productions["<F>"] = "<Q><V><F> | " + sets["connectives"][-1] + "<F> | (<F><K><F>) | <A>"
    productions["<K>"] = " | ".join(sets["connectives"][:-1])
    productions["<Q>"] = " | ".join(sets["quantifiers"])
    if predicates:
        productions["<A>"] = "<P>(<X>) | (<T>"+ sets["equality"][0] + "<T>)"
        productions["<P>"] = " | ".join(predicates.keys())
        predlist = []
        for p in predicates.keys():
            arityvar = ",".join(["<V>"]*predicates[p])
            predlist.append(arityvar)
        productions["<X>"] = " | ".join(predlist)
    else:
        productions["<F>"] = "<Q><V><F> | " + sets["connectives"][-1] + "<F> | (<F><K><F>) | (<T>"+ sets["equality"][0] + "<T>)"     
    productions["<T>"] = "<C> | <V>"
    if not sets["constants"]:
        if not sets["variables"]:
            productions = {}
        else:
            productions.pop('<T>', None)
            if predicates:
                productions["<A>"] = "<P>(<X>) | (<V>"+ sets["equality"][0] + "<V>)"
            else:
                productions["<F>"] = "<Q><V><F> | " + sets["connectives"][-1] + "<F> | (<F><K><F>) | (<V>"+ sets["equality"][0] + "<V>)"    
    else:
        productions["<C>"] = " | ".join(sets["constants"])
    if not sets["variables"]:
        if not sets["constants"]:
            productions = {}
        else:
            productions["<F>"] = sets["connectives"][-1] + "<F> | (<F><K><F>) | (<C>"+ sets["equality"][0] + "<C>)"
            productions.pop('<P>', None)
            productions.pop('<A>', None)
            productions.pop('<X>', None)
            productions.pop('<Q>', None)
            productions.pop('<T>', None)
    else:
        productions["<V>"] = " | ".join(sets["variables"])
    return productions

def outputGrammar():
    output_file = open("grammar.txt", "w")
    output_file.write("Terminal symbols:\n" + ", ".join(symbols) + "\n\nNon-Terminal symbols:\n" + ", ".join(list(productions.keys())) + "\n\nProductions:\n")
    for key, value in productions.items():
        output_file.write(key + " -> " + value + "\n")
    output_file.close()

def modifyFormula():
    formula = " ".join(sets["formula"])
    formula = formula.replace("(", " ( ")
    formula = formula.replace(")", " ) ")
    formula = formula.replace(",", " , ")
    sets["formula"] = formula.split()
    if sets["formula"].count('(') != sets["formula"].count(')'):
        updateLog(2, "Unbalanced parenthesis in formula")

def parseFormula():
    formula = sets["formula"].copy()
    postfix = []
    stack = []
    while formula:
        item = formula.pop(0)
        if item in sets["quantifiers"]:
            if formula[0] not in sets["variables"]:
                updateLog(2, item + " " + formula[0] + " is not a valid formula")
            stack.extend([formula.pop(0), item])
        elif item in sets["connectives"] + sets["equality"]:
            while (stack[-1] == sets["connectives"][-1]) or (stack[-1] in sets["quantifiers"]):
                if stack[-1] == sets["connectives"][-1]:
                    postfix.append(stack.pop())
                else:
                    postfix.append(stack.pop())
                    postfix.append(stack.pop())
            stack.append(item)
        elif item in sets["variables"] + sets["constants"]:
            postfix.append(item)
        elif item == '(':
            stack.append(item)
        elif item == ')':
            try:
                while stack[-1] != '(':
                    postfix.append(stack.pop())
                stack.pop()
            except IndexError:
                updateLog(2, "Invalid parenthesis in formula")
        elif item in predicates.keys():
            if formula.pop(0) != '(':
                updateLog(2, "Predicate must be followed by left parenthesis")
            try:
                ctr = 0
                while formula[0] != ')':
                    if formula[0] in sets["variables"]:
                        postfix.append(formula.pop(0))
                        ctr += 1
                    elif formula[0] == ',':
                        formula.pop(0)
                    else:
                        updateLog(2, formula.pop(0) + " is not valid inside predicate.")
                formula.pop(0)
                if ctr != predicates[item]:
                    updateLog(2, "Predicate "+ item + " in formula does not match defined arity. Expected " + str(predicates[item]) + ", recieved " + str(ctr))
                postfix.append(item)
            except IndexError:
                updateLog(2, "Predicate atom must end in right parenthesis")
        else:
            updateLog(2, "Undefined symbol " + item + " in formula")
    stack.reverse()
    postfix += stack
    makeTree(postfix)

def makeTree(expr):
    res = []
    G = nx.DiGraph()
    labels = {}
    n = 0
    while expr:
        item = expr.pop(0)
        if item in sets["variables"] + sets["constants"]:
            G.add_node(n)
        elif item in predicates.keys():
            i = 0
            while i < predicates[item]:
                G.add_edge(n, res.pop())
                i += 1
        elif item == sets["connectives"][-1]:
            G.add_edge(n, res.pop())
        elif item in sets["connectives"]:
            G.add_edge(n, res.pop())
            G.add_edge(n, res.pop())
        elif item in sets["equality"]:
            operands = [labels[res[-1]], labels[res[-2]]]
            if not set(operands).issubset(set(sets["variables"] + sets["constants"])):
                updateLog(2, operands[1] + " " + item + " " + operands[0] + " is not a valid formula")
            G.add_edge(n, res.pop())
            G.add_edge(n, res.pop())
        elif item in sets["quantifiers"]:
            item += " " + expr.pop(0)
            G.add_edge(n, res.pop())
        res.append(n)
        labels[n] = item
        n += 1
    pos = graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_lables=False)
    nx.draw_networkx_labels(G, pos, labels)
    plt.savefig("tree.png")

sets = {
    "variables" : [],
    "constants" : [],
    "predicates" : [],
    "equality" : [],
    "connectives" : [],
    "quantifiers" : [],
    "formula" : []
}

getInput()
predicates = setPredicates()

symbols = sets["variables"] + sets["constants"] + list(predicates.keys())
if len(symbols) != len(set(symbols)):
    updateLog(1,"Variables, constants and predicates must have different names")
if len(sets["equality"]) != 1:
    updateLog(1,"Equality must have exactly one element")
if len(sets["connectives"]) != 5:
    updateLog(1,"Connectives must have exactly 5 elements")
if len(sets["quantifiers"]) != 2:
    updateLog(1,"Quantifiers must have exactly 2 elements")
symbols += sets["equality"] + sets["connectives"] + sets["quantifiers"]

productions = setProductions()
outputGrammar()
modifyFormula()
parseFormula()
updateLog()
