import re
var_pattern = re.compile("^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]*$")
researched_word = r"string@řetězec\032s\032lomítkem\032\092\032a\010novým\035řádkem"
pattenr = re.compile("ek")

print(re.fullmatch(r"^string@(.*(\\[0-9]{3})?)*$", researched_word))

all_occurences = re.findall(r"\\[0-9]{3}", researched_word)
print(all_occurences)

for occurence in all_occurences:
    researched_word = researched_word.replace(occurence, chr(int(occurence[1:])))
    
print(researched_word)