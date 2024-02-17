import re
var_pattern = re.compile("^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]*$")
print(re.fullmatch(var_pattern, "TF@_xA3433"))