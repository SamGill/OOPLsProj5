import sys
import importlib

#Error
class GroveError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

#Language Definition
var_table = {}

#Expressions
class Expr:
    pass

class Num(Expr):
    def __init__(self, value):
        self.value = value
    def eval(self):
        return self.value

class Name(Expr):
    def __init__(self, name):
        self.name = name
    def getName(self):
        return self.name
    def eval(self):
        
        if self.name in var_table:
            return var_table[self.name]
        else:
            raise GroveError("CALC: undefined variable " + self.name)

class StringLiteral(Expr):
    def __init__(self, value):
        self.value = value
    def eval(self):
        return self.value

class Addition(Expr):
    def __init__(self, child1, child2):
        self.child1 = child1
        self.child2 = child2
        if not isinstance(self.child1, Expr):
            raise GroveError("CALC: expected expression but recieved " + str(type(self.child1)))
        if not isinstance(self.child2, Expr):
            raise GroveError("CALC: expected expression but recieved " + str(type(self.child2)))
        if type(self.child1.eval()) != type(self.child2.eval()):
            raise GroveError("CALC: Addition on differing types. left type: " + str(type(self.child1)) + " but right type: " + str(type(self.child2)))
    def eval(self):
        return self.child1.eval() + self.child2.eval()

class MethodCall(Expr):
    def __init__(self, objectName, methodName, *args):
        self.objectName = objectName
        self.methodName = methodName
        self.args = args
    def addArg(self, expr):
        pass
    def eval(self):
        vals = [i.eval() for i in self.args]
        check(self.objectName.getName() in var_table, "the value: " + str(self.objectName.getName()) + " is not defined")
        return getattr(var_table[self.objectName.getName()], self.methodName.getName())(*vals)

#Statements
class Stmt:
    pass

class SetAssignment(Stmt):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        if not isinstance(self.expr, Expr):
            raise GroveError("CALC: expected expression but recieved " + str(type(self.expr)))
        if not isinstance(self.name, Name):
            raise GroveError("CALC: expected name but recieved " + str(type(self.expr)))
            
    def eval(self):
        var_table[self.name.name] = self.expr.eval()
        

class SetConstructor(Stmt):
    def __init__(self, varname, obj):
        self.varname = varname
        self.obj = obj
    
    def eval(self):
        try:
            check(type(eval(self.obj)) == type(object), "Expected an object type for new command")
            var_table[self.varname.name] = eval(self.obj)()
        except:
            raise GroveError("Grove: Could not set object properly")
class Exit(Stmt):
    def eval(self):
        sys.exit()
        pass

class Import(Stmt):
    def __init__(self, name):
        self.name = name
    def eval(self):
        try:
            mod = importlib.import_module(self.name)
            globals()[self.name] = mod
        except:
            raise GroveError("GROVE: error importing the module")
        

#Interpreter
def parse(s):
    """ Return an object representing a parsed command
        Throws ValueError for improper syntax """
    (root, remaining_tokens) = parse_tokens(s.split())
    
    check(len(remaining_tokens) == 0, "Expected end of command but found '" + " ".join(remaining_tokens) + "'")
    return root
        
def parse_tokens(tokens):
    """ Returns a tuple:
        (an object representing the next part of the expression, the remaining tokens)
    """
    check(len(tokens) > 0)
    start = tokens[0]
    #Num
    if is_int(start):
        return ( Num(int(start)), tokens[1:] )
    #String
    elif start.startswith('"') and start.endswith('"'):
        check( not ' ' in start, "No whitespace can be in string literal")
        check( not '"' in start[1:-1], "No quotes can be in string literal")
        return ( StringLiteral(start[1:-1]), tokens[1:] )
    #Addition
    elif start == "+":
        expect(tokens[1], "(")
        (child1, tokens) = parse_tokens(tokens[2:])
        #print(tokens)
        check(len(tokens) > 1)
        expect(tokens[0], ")")
        expect(tokens[1], "(")
        (child2, tokens) = parse_tokens(tokens[2:])
        check(len(tokens) > 0)
        expect(tokens[0], ")")
        
        #if isinstance(child1, Num
        
        return ( Addition(child1, child2), tokens[1:])
    #Method
    elif start == "call":
        check(len(tokens[1:]) > 0, "Invalid call syntax for call")
        check(tokens[1] == "(", "Invalid syntax for call statement. Expected '(' but got: " + str(tokens[1]))

        check(len(tokens[2:]) > 0, "Not enough arguments for call function")
        (objectname, tokens) = parse_tokens(tokens[2:])
        
        (methodname, tokens) = parse_tokens(tokens[0:])
        #call = MethodCall(objectname, methodname)
        
        #grab args
        methodArgs = []
        check(len(tokens) > 0, "call function never had closing parenthesis")
        while tokens[0] != ")":
            #print("Before tokens: " + str(tokens))
            check(len(tokens) > 1, "call function never had closing parenthesis")
            (nextArg, tokens) = parse_tokens(tokens[0:])
            
            #print(nextArg)
            #print("After tokens: " + str(tokens))

            methodArgs.append(nextArg)
            
            
        
        return (MethodCall(objectname, methodname, *methodArgs), tokens[1:])
        
    #Set
    elif start == "set":
        (varname, tokens) = parse_tokens(tokens[1:])
        check(len(tokens) > 0, "incomplete set expression")
        expect(tokens[0], "=")
        if tokens[1] == "new":
            obj = tokens[2]
            return ( SetConstructor(varname, obj), tokens[3:] )
        else:
            (child, tokens) = parse_tokens(tokens[1:])
            return ( SetAssignment(varname, child), tokens )
    #Exit
    elif start == "quit" or start == "exit":
        return ( Exit(), tokens[1:] )
    #import
    elif start == "import":

        
        check(len(tokens) > 1, "must provide module to import")
        name = tokens[1]
        #(name, tokens) = parse_tokens(tokens[2:])
        return ( Import(name), tokens[2:] )
    else:
        #print(start)
        isAlphaOr_ = start.replace("_", "a").isalnum() and not is_int(start[0]) and not "\"" in start
        check(isAlphaOr_, "Variable names must be alphabetic")
        return ( Name(start), tokens[1:] )

# Utility methods for handling parse errors
def check(condition, message = "Unexpected end of expression"):
    """ Checks if condition is true, raising a ValueError otherwise """
    if not condition:
        raise GroveError("CALC: " + message)
        
def expect(token, expected):
    """ Checks that token matches expected
        If not, throws a ValueError with explanatory message """
    if token != expected:
        check(False, "Expected '" + expected + "' but found '" + token + "'")
        
def is_expr(x):
    if not isinstance(x, Expr):
        check(False, "Expected expression but found " + str(type(x)))
# Checking for integer        
def is_int(s):
    """ Takes a string and returns True if in can be converted to an integer """
    try:
        int(s)
        return True
    except ValueError:
        return False

#Console
while True:
    try:        
        ln = input("Grove>> ")
        root = parse(ln)
        res = root.eval()
        if not res is None:
            print(res)
    except GroveError as ge:
        print(ge)
