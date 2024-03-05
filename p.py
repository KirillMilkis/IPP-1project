import re
var_pattern = re.compile("^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]*$")
researched_word = r"string@řetězec\032s\032lomítkem\032\092\032a\010novým\035řádkem"
pattenr = re.compile("ek")
label_pattern = re.compile(r"^[a-zA-Z$&%*!?-][\S]*$")


splitted_list = re.split("#", "fff#")

print(type(splitted_list))
print(splitted_list)