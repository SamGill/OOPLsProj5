
# A hack to avoid running the interpreter in grove.py
if __name__ == "__main__":
    __name__ = "notmain"
exec(open("grove.py").read())
print("stuff")
# A hack to avoid running the interpreter in grove.py
if __name__ == "notmain":
    __name__ = "__main__"
    


def check_no_parse(filename="no_parse.txt"):
    with open(filename) as f:
        for ln in f:
            try:
                parse(ln)
                print("Failed to raise a parsing error for following line:")
                print(ln)
                raise Exception()
            except GroveError:
                pass
                
        
                
                
def check_no_eval(filename="no_eval.txt"):
    with open(filename) as f:
        for ln in f:
            try:
                root = parse(ln)
                root.eval()
                print("Failed to raise an evaluation error for following line:")
                print(ln)
                raise Exception()
            except GroveError:
                pass
                
                
if __name__ == "__main__":
    print("Checking that errors are caught...")
    check_no_parse()
    check_no_eval()
    print("Tests passed")
    
