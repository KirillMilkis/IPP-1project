import re
var_pattern = re.compile("^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]*$")
pattenr = re.compile("ek")
print(re.match(pattenr, "dekrff"))
