_all_ = ({},{},{})
_avail_ = ({},{},{})
_loaded_ = ({},{},{})

def isfloat(self):
    try:
        float(self)
        return True
    except ValueError: return False

class AddError(Exception): pass

def cacheAdd(add):
    _loaded_[0][add.name] = add
def cacheType(typ):
    _loaded_[0][typ.name] = typ
def cacheFunc(func):
    _loaded_[0][func.name] = func

def getAdd(name):
    try:
        ret = _avail_[0][name]
        for add in ret.adds: _avail_[0][add.name] = add
        for typ in ret.types: _avail_[1][typ.name] = typ
        for func in ret.funcs: _avail_[2][func.name] = func
        return ret
    except KeyError: raise AddError("Unable to locate addition '%s'" % name)
def getFunc(name):
    try:
        return _avail_[2][name]
    except KeyError: raise NameError("Function '%s' is not defined" % name)
class uadd:
    def __init__(self, name:str, adds, types, funcs, *, available:bool=False):
        self.name, self.adds, self.types, self.funcs, self.avail = name, adds, types, funcs, available
        _all_[0][self.name] = self
        if self.avail: _avail_[0][self.name] = self
    def __str__(self):
        return self.name
class utype:
    def __init__(self, name:str, inherits, *, base:bool=False):
        self.name, self.inherits, self.base = name, inherits, base
        _all_[1][self.name] = self
        #if self.base: _avail_[1][self.name] = self
    def __str__(self):
        return self.name
class ufunc:
    def __init__(self, name:str, function):
        self.name, self.func = name, function
        _all_[2][self.name] = self
    def __call__(self, *args):
        return self.func(*args)
    def __str__(self):
        return self.name

def obj(otype, name, values=[]):
    values = [str(i) for i in values]
    if len(values) > 0: return "<%s object '%s' with assigned values (%s)>" % (otype, name, ", ".join(values))
    else: return "<%s object '%s'>" % (otype, name)
def inst(which, values): return "<%s instruction with parameters (%s)>" % (which, ", ".join(values))
def char(which):
    if which == ",": return "<End of instruction>"
    else: raise SyntaxError("Invalid syntax")
def biobj(typ, data):
    if typ == str: return "<str %s>" % data
    elif typ == int: return "<int %s>" % data
    elif typ == float: return "<float %s>" % data
    else: raise SyntaxError("Invalid syntax")
def itemsBrackets(string):
    if not (string.startswith("[") and string.endswith("]")): raise SyntaxError("Unclosed bracket set")
    return [block(it) for it in string.replace("[","").replace("]","").split(";")]

def block(item):
    item = item.replace(" ","").split("//")[0]
    if item.startswith("$"):
        values = list(item.split("!"))
        del values[0]
        values = [block(j) for j in values]
        cacheAdd(getAdd(item.split("!")[0].replace("$","")))
        return obj("add", item.split("!")[0].replace("$",""), values)
    elif item.startswith(">>"):
        func = getFunc(item.split("[")[0].replace(">>",""))
        values = list(item.split("["))
        del values[0]
        values[0] = "[" + values[0]
        values = "[".join(values)
        return obj("func", func.name, itemsBrackets(values))
    elif item.startswith('"'):
        if item.endswith('"'): return biobj(str, item)
        else: raise SyntaxError("Unclosed quote set")
    elif item.isdigit(): return biobj(int, item)
    elif isfloat(item): return biobj(float, item)
    else: raise SyntaxError("Invalid syntax")

input_ = ufunc("input", input)
print_ = ufunc("print", print)
type_ = utype("type", [], base=True)
str_ = utype("str", [])
list_ = utype("list", [])
NOTE_ = uadd("NOTE", [], [], [])
CONTRAST_ = uadd("CONTRAST", [], [], [])
UNION_ = uadd("UNION", [NOTE_, CONTRAST_], [type_, list_, str_], [print_, input_], available=True)

def interpret(inp:str):
    cont = list(inp.replace("\n",",").split(","))
    out = "<SOF>"
    delcount = 0
    for i in range(len(cont)):
        cont[i-delcount] = cont[i-delcount].split("#")[0]
        if cont[i-delcount].replace(" ","") == "": del cont[i-delcount]; delcount += 1
    cmt = False
    for i, lineno in zip(cont, range(len(cont))):
        out += block(i) + char(",")
    out += "<EOF>"
    return out

print(interpret("""
$UNION,$CONTRAST
>>print["stuff"]
"""))
