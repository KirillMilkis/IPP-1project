import sys
import re
import xml.etree.ElementTree as ET

ERROR_MISSING_HEADER, ERROR_OPERATION_CODE, ERROR_OTHER, ERROR_ARGS = 21, 22, 23, 10


class ProcessedInstrunction:
    def __init__(self, order, opcode, arg_count = 3):
        self.order = order
        self.opcode = opcode
        self.args = {}
        self.args_types = {}
        self.arg_count = arg_count

    def arg_set(self, arg, arg_type):
        for i in range(1, self.arg_count):
            if i in self.args().keys():
                continue
            self.args[i] = arg
            self.args_types[i] = arg_type
    
    @property
    def args(self, order):
        return self.args[order]

    @property
    def args_types(self, order):
        return self.args_types[order]

    def begin_xml_stdout(self, xml_root):

        xml_tree = ET.Element('program')

    def create_instr_line(self):
        
        instrunction =  ET.SubElement(xml_doc, order = self.order, opcode = self.opcode)
        for num in range(1,self.max_arg_count):
            if hasattr(self,f"arg{num}"):
                ET.subElement(instruction, 'arg{num}', type = self.arg1_type, text = self.args[num])
            else:
                return ERROR_OTHER

    def write_instr_line(self):

        xml_tree.write(sys.stdout, encoding='unicode')
        

    


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

    def __init__(self, line = 0, frame = "GF", active_stdin = True, current_line = ""):
        self.line = line
        self.__frame = frame
        self.active_stdin = active_stdin
        self.current_line = current_line
        self.instr_num = 1

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
            current_instr.arg_set(cut_const(self,self.line[0]), "int")
            print("writing int to xml")
        elif re.fullmatch("^bool@(bool|true)$", researched_word):
            current_instr.arg_set(cut_const(self,self.line[0]), "bool")
            # write bool to xml
            print("writing bool to xml")
        elif re.fullmatch("^string@.([\p{L}]*[0-9]*(\\[0-9]{3})?))", researched_word):
            current_instr.arg_set(cut_const(self,self.line[0]), "string")
            #write string to xml
            print("writing string to xml")
        elif re.fullmatch("^nil@nil$", researched_word):
            current_instr.arg_set(cut_const(self,self.line[0]), "nil")
            #write nil to xml
            print("writing nil to xml")

    def parse_instr(self, instr_sample):

        researched_line = self.current_line

        label_pattern = re.compile("^[a-zA-Z$&%*!?-][\S]*$")
        var_pattern = re.compile("^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]**$")
        const_pattern = re.compile("^(bool|nil|int|string)@[a-zA-Z_$&%*!?-][\S]**$")

        current_instr = ProcessedInstrunction(self.instr_num, instr_sample[0].higher)

        for key_word in instr_sample[1:]:

            if not researched_line[0]:
                return ERROR_OTHER

            if key_word == "var":
                
                if (re.fullmatch(var_pattern, researched_line[0])):
                    current_instr.arg_set(researched_line[0], 'var')
                    researched_line.pop()
                else:
                    return ERROR_OTHER

            elif key_word == "symb":
               
                if (re.fullmatch(const_pattern, researched_line[0])):
                    self.parse_const(self, current_instr, researched_line[0])
                    researched_line.pop()
                elif (re.fullmatch(var_pattern, researched_line[0])):
                    current_instr.arg_set(researched_line[0], 'var')
                    researched_line.pop()
                else:
                    return ERROR_OTHER
                    
            elif key_word == "label":

                if(re.fullmatch(label_pattern, researched_line[0])):
                    current_instr.arg_set(researched_line[0], 'label')
                    researched_line.pop()
                else:
                    return ERROR_OTHER
                    

        if self.line:
            if self.line == "#":
                self.line.clean()
                return 
            else:
                return ERROR_OTHER  
                

    def get_next_line(self):

        tokens = []

        for word in sys.stdin.readline().split():
            tokens.append(word)

        if tokens:    
            self.line = tokens.copy()
            return True

        return False    


    def parse_line(self):

        # check for comment 
        if self.line[0].lower == "#": 
                return 0
        
        # check for ipp24 instrunction_samples

        found = False
        for inst in Parser.instruction_samples:

            a = self.line[0].lower()
            print(a)
            if self.line[0].lower() == inst[0].lower():
                found = True
                self.parse_instr(inst)
                continue

        #  some instruction problems --> exit with error
        if not found: 
            return ERROR_OPERATION_CODE
        
        return 0
        

def check_func(return_code):
    if return_code != 0 and return_code != None:
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
                exit_prog(0)

def main():

        args = sys.argv
        if len(args) > 1:
            if check_func(read_args(args)) is None:
                sys.exit(0)
        
        ipp24_parser = Parser(0,"GF", True, "")
        
        while ipp24_parser.get_next_line() != False:
            check_func(ipp24_parser.parse_line())


main()
print('Done')






