import sys
import re
import xml.etree.ElementTree as ET

ERROR_MISSING_HEADER, ERROR_OPERATION_CODE, ERROR_OTHER, ERROR_ARGS = 21, 22, 23, 10
READING_END = 5

class ProcessedInstrunction:
    def __init__(self, order, opcode, arg_count = 3):
        self.order = order
        self.opcode = opcode
        self.args = {}
        self.args_types = {}
        self.arg_count = arg_count
        self.xml_tree = None
        self.instr_tree = None

    
    
    # @property
    # def args(self, order):
    #     return self.args[order]

    # @args.setter
    # def args(self, value):
    #     raise AttributeError("Use arg_set method to set args.")

    def arg_set(self, arg, arg_type):
        for i in range(1, self.arg_count):
            if i in self.args.keys():
                continue
            self.args[i] = arg
            self.args_types[i] = arg_type
            break

    # @property
    # def args_types(self, order):
    #     return self.args_types[order]

    # def begin_xml_stdout(self):

    #     self.xml_tree = ET.Element('program')

    def create_instr_line(self, xml_tree):
        self.instr_tree =  ET.SubElement(xml_tree, 'instruction', order = str(self.order), opcode = self.opcode)

    def rec_to_instr_line(self):
       
        for num in range(1,self.arg_count):
            if not hasattr(self,f"arg{num}"):
                ET.SubElement(self.instr_tree, f'arg{num}', type = self.args_types[num], text = self.args[num])
            
    
    def get_instr_tree(self):
        return self.instr_tree

    # def write_instr_line(self):

    #     self.xml_tree.write(sys.stdout, encoding='unicode')
        

    


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

    def __init__(self, line = 0, frame = "GF", active_stdin = True, current_line = "", language = 'IPPcode24'):
        self.line = line
        self.__frame = frame
        self.active_stdin = active_stdin
        self.current_line = current_line
        self.instr_num = 1
        self.language = language

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


    def parse_instr(self, instr_sample):

        researched_line = self.current_line

        label_pattern = re.compile(r"^[a-zA-Z$&%*!?-][\S]*$")
        var_pattern = re.compile(r"^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\S]*$")
        const_pattern = re.compile(r"^(bool|nil|int|string)@[a-zA-Z_$&%*!?-][\S]*$")

        current_instr = ProcessedInstrunction(self.instr_num, instr_sample[0].upper())
        xml_tree = ET.Element('program', language = self.language)
        current_instr.create_instr_line(xml_tree)
       
        for key_word in instr_sample[1:]:

            try:
                t = researched_line[0]
            except IndexError:
                return ERROR_OTHER
            

            if key_word == "var":
                
                if (re.fullmatch(var_pattern, researched_line[0])):
                    current_instr.arg_set(researched_line[0], 'var')
                    researched_line.pop(0)
                    
                else:
                    return ERROR_OTHER

            elif key_word == "symb":
               
                if (re.fullmatch(const_pattern, researched_line[0])):
                    self.parse_const(self, current_instr, researched_line[0])           
                    researched_line.pop(0)

                elif (re.fullmatch(var_pattern, researched_line[0])):
                    current_instr.arg_set(researched_line[0], 'var')
                    researched_line.pop(0)

                else:
                    return ERROR_OTHER
                    
            elif key_word == "label":

                if(re.fullmatch(label_pattern, researched_line[0])):
                    current_instr.arg_set(researched_line[0], 'label')
                    researched_line.pop(0)

                else:
                    return ERROR_OTHER
                    

        if self.line:
            if self.line == "#":
                self.line.clean()
                return 
            else:
                return ERROR_OTHER  
            
        
        current_instr.rec_to_instr_line()
        ET.ElementTree(xml_tree).write(sys.stdout, encoding='unicode')

        return 0
                

    def get_next_line(self):

        tokens = []

        for word in sys.stdin.readline().split():
            tokens.append(word)

        if tokens:    
            self.current_line = tokens.copy()
            return 0

        return READING_END    


    def parse_line(self):

        try:
            a = self.current_line[0]
            b = Parser.instruction_samples[0]
        except IndexError:
            return ERROR_OTHER

        # check for comment 
        if self.current_line[0].lower == "#": 
                return 0
        
        # check for ipp24 instrunction_samples

        found = False
        for inst in Parser.instruction_samples:

            print('function parse_line')
            if self.current_line[0].lower() == inst[0].lower():
                found = True
                self.current_line.pop(0)
                check_func(self.parse_instr(inst))
                break

        #  some instruction problems --> exit with error
        if not found: 
            return ERROR_OPERATION_CODE
        
        return 0
    
    def parse_header(self, header):
        
        if len(self.current_line) == 1 and self.current_line[0] == header:
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
        
        check_func(ipp24_parser.get_next_line())
        check_func(ipp24_parser.parse_header('.IPPcode24'))
        while check_func(ipp24_parser.get_next_line()) != READING_END:
            check_func(ipp24_parser.parse_line())


main()
print('Done')






