import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom

ERROR_MISSING_HEADER, ERROR_OPERATION_CODE, ERROR_OTHER, ERROR_ARGS = 21, 22, 23, 10
READING_END = 5

class ProcessedInstrunction:
    def __init__(self, order, opcode, arg_count):
        self.order = order
        self.opcode = opcode
        self.args = []
        self.arg_count = 0
        self.instr_tree = None

    def arg_set(self, arg, arg_type):
        self.arg_elem = []
        self.arg_elem.append([arg,arg_type])

        self.arg_count+=1
        arg_xml_elem = ET.SubElement(self.instr_tree, f'arg{self.arg_count}', type = self.arg_elem[self.arg_count-1][1])
        arg_xml_elem.text = self.arg_elem[self.arg_count-1][0]

    def create_instr_line(self, xml_tree):
        self.instr_tree =  ET.SubElement(xml_tree, 'instruction', order = str(self.order), opcode = self.opcode)
        # self.instr_tree.text = "\n"

    # def rec_to_instr_line(self):
       
    #     # for num in range(0,self.arg_count):
    #     #     if not hasattr(self,f"arg{num}"):
    #     #         arg_element = ET.SubElement(self.instr_tree, f'arg{num}', type = self.args_types[num])
    #     #         arg_element.text = self.args[num]
            
    
    def get_instr_tree(self):
        return self.instr_tree



class Parser:

    instruction_samples = [
        ['MOVE', 'var', 'symb'],
        ['CREATEFRAME'],
        ['PUSHFRAME'],
        ['POPFRAME'],
        ['DEFVAR', 'var'],
        ['CALL', 'label'],
        ['RETURN'],
        ['PUSHS', 'symb'],
        ['POPS', 'var'],
        ['ADD', 'var', 'symb', 'symb'],
        ['SUB', 'var', 'symb', 'symb'],
        ['MUL', 'var', 'symb', 'symb'],
        ['IDIV', 'var', 'symb', 'symb'],
        ['LT', 'var', 'symb', 'symb'],
        ['GT', 'var', 'symb', 'symb'],
        ['EQ', 'var', 'symb', 'symb'],
        ['AND', 'var', 'symb', 'symb'],
        ['OR', 'var', 'symb', 'symb'],
        ['NOT', 'var', 'symb'],
        ['INT2CHAR', 'var', 'symb'],
        ['STRI2INT', 'var', 'symb', 'symb'],
        ['READ', 'var', 'type'],
        ['WRITE', 'symb'],
        ['CONCAT', 'var', 'symb', 'symb'],
        ['STRLEN', 'var', 'symb'],
        ['GETCHAR', 'var', 'symb', 'symb'],
        ['SETCHAR', 'var', 'symb', 'symb'],
        ['TYPE', 'var', 'symb'],
        ['LABEL', 'label'],
        ['JUMP', 'label'],
        ['JUMPIFEQ', 'label', 'symb', 'symb'],
        ['JUMPIFNEQ', 'label', 'symb', 'symb'],
        ['EXIT', 'symb'],
        ['DPRINT', 'symb'],
        ['BREAK']
        ]

    errors = {
        "ERROR_MISSING_HEADER": 21,
        "ERROR_OPERATION_CODE": 22,
        "ERROR_OTHER": 23
        }

    frame_type = {
        "GF": 100,
        "LF": 101,
        "TF": 102
        }

    def __init__(self, line = 0, frame = "GF", active_stdin = True, current_line = "", language = 'IPPcode24', language_header = '.IPPcode24'):
        self.line_num = line
        self.__frame = frame
        self.active_stdin = active_stdin
        self.read_header = False
        self.current_line = current_line
        self.instr_num = 1
        self.language = language
        self.language_header = language_header
        
    def createXMLtree(self):
        self.xml_tree = ET.Element('program', language = self.language)

    def printXMLtree(self):
        # ET.ElementTree(self.xml_tree).write(sys.stdout, encoding='unicode')
        # print(ET.tostring(self.xml_tree, encoding='utf8').decode('utf8'))
        print(xml.dom.minidom.parseString(ET.tostring(self.xml_tree, encoding='utf-8')).toprettyxml(indent="    "))

    @property
    def frame(self):
        return self.__frame

    @frame.setter
    def change_frame(self, required_frame):
        self.__frame = self.frame_type[required_frame]

    def cut_const(self, const):
        cutted_const = re.split('@', self.line[0], 1)
        if cutted_const[1]:
            return cutted_const[1]
        else:
            return cutted_const[0]


    def parse_const(self, current_instr, researched_word):

        if re.fullmatch("^int@-?[0-9]*$", researched_word):
            current_instr.arg_set(self.cut_const(self.line[0]), "int")

        elif re.fullmatch("^bool@(bool|true)$", researched_word):
            current_instr.arg_set(self.cut_const(self.line[0]), "bool")

        elif re.fullmatch(r"^string@.([\w]*[0-9]*(\\[0-9]{3})?))", researched_word):
            current_instr.arg_set(self.cut_const(self.line[0]), "string")

        elif re.fullmatch("^nil@nil$", researched_word):
            current_instr.arg_set(self.cut_const(self.line[0]), "nil")


    def parse_instr_args(self, instr_sample):

        label_pattern = re.compile(r"^[a-zA-Z$&%*!?-][\S]*$")
        var_pattern = re.compile(r"^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]*$")
        const_pattern = re.compile(r"^(bool|nil|int|string)@[a-zA-Z_$&%*!?-][\S]*$")

        current_instr = ProcessedInstrunction(self.instr_num, instr_sample[0].upper(), len(self.current_line))
        current_instr.create_instr_line(self.xml_tree)
       
        for key_word in instr_sample[1:]:

            try:
                t = self.current_line[0]
            except IndexError:
                return ERROR_OTHER
            

            if key_word == "var":
                
                if (re.fullmatch(var_pattern, self.current_line[0])):
                    current_instr.arg_set(self.current_line[0], 'var')
                    self.current_line.pop(0)
                    
                else:
                    return ERROR_OTHER

            elif key_word == "symb":
               
                if (re.fullmatch(const_pattern, self.current_line[0])):
                    self.parse_const(current_instr, self.current_line[0])           
                    self.current_line.pop(0)

                elif (re.fullmatch(var_pattern, self.current_line[0])):
                    current_instr.arg_set(self.current_line[0], 'var')
                    self.current_line.pop(0)

                else:
                    return ERROR_OTHER
                    
            elif key_word == "label":

                if(re.fullmatch(label_pattern, self.current_line[0])):
                    current_instr.arg_set(self.current_line[0], 'label')
                    self.current_line.pop(0)

                else:
                    return ERROR_OTHER
                   

        return 0
                

    def get_next_line(self):

        tokens = []

        for word in sys.stdin.readline().split():

            tokens.append(word)
            
        if tokens:    
                self.current_line = tokens.copy()
                return 0
        
        return READING_END


    def is_comment(self):
        if re.match(r"^#*", self.current_line[0]):
            return True
        else:
            return False

    def parse_line(self):
      
        #check for header and comment after header
        while not self.read_header:
            if self.is_comment():
                return 0
            elif self.current_line[0] == self.language_header:
                self.read_header = True
                return 0
            else:
                return ERROR_MISSING_HEADER

        if not self.read_header:
            check_func(self.parse_header())
            if self.current_line:
                if self.is_comment():
                    return 0
                else:
                    return ERROR_OTHER
            return 0
        
        # check for ipp24 instrunction_samples
        found = False
        for inst in Parser.instruction_samples:

            if self.current_line[0].lower() == inst[0].lower():
                found = True
                self.current_line.pop(0)
                check_func(self.parse_instr_args(inst))
                self.instr_num+=1  
                break
        
        #check for comment before or after opeeration code
        if self.is_comment():
            return 0
        
        #  some instruction problems --> exit with error
        if not found: 
            return ERROR_OPERATION_CODE

        
        return 0
    
    def parse_header(self):
        
        if  self.current_line[0] == self.language_header:
            self.read_header = True
            self.current_line.pop(0)
            return 0
        else:
            return ERROR_MISSING_HEADER
        

def check_func(return_code):
    if return_code >= 10:
        print(f"ERROR: {return_code}")
        sys.exit(return_code)
    else:
        return return_code


def read_args(args):
    
            if (args[1] != '--help') or (args[1] == '--help' and len(args) > 2):
                return ERROR_ARGS
            elif args[1] == '--help':
                print("\nSkript typu filtr (parse.py v jazyce Python 3.10) načte ze standardního\n" 
                "vstupu zdrojový kód v IPP- code24 (viz sekce 5), zkontroluje lexikální a syntaktickou\n" 
                "správnost kódu a vypíše na standardní výstup XML reprezentaci programu\n")
                sys.exit(0)

def main():

        args = sys.argv
        if len(args) > 1:
            if check_func(read_args(args)) is None:
                sys.exit(0)
        
        ipp24_parser = Parser(0,'GF', True, '', 'IPPcode24')

        ipp24_parser.createXMLtree()
        
        while check_func(ipp24_parser.get_next_line()) != READING_END:
            check_func(ipp24_parser.parse_line())

        ipp24_parser.printXMLtree()


main()






