uadds_ = {}
availadd_ = {}
utypes_ = {}
availtype_ = {}
ufuncs_ = {}
availfunc_ = {}
mem = ({},{},{},{})

def isfloat(self):
    try:
        float(self)
        return True
    except ValueError: return False

class AddError(Exception): pass

def cacheAdd(add):
    mem[0][add.name] = add
def cacheType(typ):
    mem[1][typ.name] = typ
def cacheFunc(func):
    mem[2][func.name] = func
def getAdd(name):
    try:
        ret = availadd_[name]
        for i in ret.adds: availadd_[i.name] = i
        for i in ret.types: availtype_[i.name] = i
        for i in ret.funcs: availfunc_[i.name] = i
        return ret
    except KeyError:
        raise AddError("Unable to locate addition '%s'" % name)
def getFunc(name):
    try:
        return availfunc_[name]
    except KeyError:
        raise NameError("Function '%s' is not defined" % name)
class ufunc:
    def __init__(self, name:str, function, avail:bool=False):
        self.name = name
        self.func = function
        self.available = avail
        if self.available: availfunc_[self.name] = self
    def __call__(self, *args):
        return self.func(*args)
    def __str__(self):
        return self.name
class utype:
    def __init__(self, name:str, inherits:tuple, *, base:bool=False):
        self.name = name
        self.inherits = inherits
        self.isbase = base
class uadd:
    def __init__(self, name:str, adds, types, funcs, *, avail:bool=False):
        self.name = name
        self.adds = adds
        self.types = types
        self.funcs = funcs
        self.available = avail
        uadds_[self.name] = self
        if self.available: availadd_[self.name] = self
        
input_ = ufunc("input", input)
print_ = ufunc("print", print)
type_ = utype("type", [], base=True)
str_ = utype("str", [])
list_ = utype("list", [])
note_ = utype("note", [])
track_ = utype("track", [])
tool_ = utype("tool", [])
plugin_ = utype("plugin", [])
Plugin_ = uadd("Plugin", [], [], [])
NOTE_ = uadd("NOTE", [], [note_, track_], [])
CONTRAST_ = uadd("CONTRAST", [], [tool_], [])
UNION_ = uadd("UNION", [Plugin_, NOTE_, CONTRAST_], [type_, plugin_, list_, str_], [print_, input_], avail=True)
def obj(otype, name, values):
    values = [str(i) for i in values]
    if len(values) > 0: return "<%s object '%s' with assigned values (%s)>" % (otype, name, ", ".join(values))
    else: return "<%s object '%s'>" % (otype, name)
def inst(which, values): return "<%s instruction with parameters (%s)>" % (which, ", ".join(values))
def char(which):
    if which == ",": return "<End of instruction>"
def biobj(typ, data):
    if typ == str: return "<str %s>" % data
    elif typ == int: return "<int %s>" % data
    elif typ == float: return "<float %s>" % data
    else: raise SyntaxError("Invalid syntax")
def itemsBrackets(string):
    if not (string.startswith("[") and string.endswith("]")): raise SyntaxError("Unclosed bracket set")
    return [block(it) for it in string.replace("[","").replace("]","").split(";")]
content=list(input().replace("\\n",",").split(","))
output="<SOF>"

def block(item):
    item = item.replace(" ", "").split("//")[0]
    
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

delcount = 0
for i in range(len(content)):
    content[i-delcount] = content[i-delcount].split("#")[0]
    if content[i-delcount].replace(" ","") == "": del content[i-delcount]; delcount += 1
cmt = False
for i, lineno in zip(content, range(len(content))):
    output += block(i)
    output += char(",")
output += "<EOF>"
print(output)
print(mem)
