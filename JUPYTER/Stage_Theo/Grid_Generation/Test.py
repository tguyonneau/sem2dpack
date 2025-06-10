import os

dir = os.path.dirname(__file__)
script = dir+'/Grid_Generation_Script.py'

with open(script) as f:
    code = f.read()

var = {}
var["dir_script"] = dir

for i in range(1):
    # var["dir_output"] = f"TEST/Case_{i}"
    var["dir_output"] = dir+'/../../../PARAM_GEN/OUTPUT'
    try:
        os.mkdir(var["dir_output"])
    except FileExistsError:
        pass
    exec(code, var)