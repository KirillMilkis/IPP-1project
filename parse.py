import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom
from enum import Enum

ERROR_INPUT_ARGS = 10
INTERNAL_ERROR = 99
ERROR_OUTPUT_FILES = 12
ERROR_INPUT_FILES = 11

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

class ProcessedInstrunction:
    def __init__(self, order, opcode, arg_count):
        self.order = order
        self.opcode = opcode
        self.args = []
        self.arg_count = 0
        self.instr_tree = None

    def arg_set(self, arg, arg_type):
        # Add new argument into the branch with one instruction
        self.args.append([arg,arg_type])
        self.arg_count+=1

        arg_xml_elem = ET.SubElement(self.instr_tree, f'arg{self.arg_count}', type = self.args[self.arg_count-1][1])
        arg_xml_elem.text = self.args[self.arg_count-1][0]

    def create_instr_line(self, xml_tree):
        # Create new instruction branch in the XML tree
        self.instr_tree =  ET.SubElement(xml_tree, 'instruction', order = str(self.order), opcode = self.opcode)    
    
    def get_instr_tree(self):
        return self.instr_tree
    

class Parser:

    ERROR_MISSING_HEADER, ERROR_OPERATION_CODE, ERROR_OTHER = 21, 22, 23
    READING_END = 5

    def __init__(self, language , language_header, read_header, current_line, instr_num, instr_samples):
        self.parser_instr_samples = instr_samples
        self.instr_num = instr_num
        self.read_header = read_header
        self.current_line = current_line
        self.language = language
        self.language_header = language_header
        self.process_line = ""
        self.parse_line_state = 0
        
    def createXMLtree(self):
        self.xml_tree = ET.Element("program", language = self.language)

    def printXMLtree(self):
        print(xml.dom.minidom.parseString(ET.tostring(self.xml_tree, encoding='utf-8')).toprettyxml(indent="    "))

    @staticmethod
    def cut_const(const):
        #Method return 2 part of the const, after @
        cutted_const = re.split('@', const, 1)
        if cutted_const[1]:
            return cutted_const[1]
        else:
            return ""

    @staticmethod    
    def cut_comment(operand):
        # Method split operand and comment if they dont have space between
        # Return list with operand and comment
        splitted_list = re.split("#", operand)
        if(len(splitted_list) > 1):
            splitted_list[1] = "#" + splitted_list[1]
        splitted_list = list(filter(None, splitted_list))
        return splitted_list

    def parse_const(self, current_instr):
        # Choose right constant pattern for parsing
        if (re.fullmatch("^int@[-+]?[0-9]+$", self.process_line[0]) or 
            re.fullmatch("^int@[-+]?0[o][0-7]+$", self.process_line[0]) or 
            re.fullmatch("^int@[-+]?0[x][0-9a-fA-F]+$", self.process_line[0])):
            current_instr.arg_set(self.cut_const(self.process_line[0]), "int")
            return 0

        elif re.fullmatch("^bool@(false|true)$", self.process_line[0]):
            current_instr.arg_set(self.cut_const(self.process_line[0]), "bool")
            return 0

        elif re.fullmatch(r"^string@([^\\#]*(\\[0-9]{3})?)+$", self.process_line[0]):
            current_instr.arg_set(self.cut_const(self.process_line[0]), "string")
            return 0
        
        elif re.fullmatch("^nil@nil$", self.process_line[0]):
            current_instr.arg_set(self.cut_const(self.process_line[0]), "nil")
            return 0
        
        # If constant has wrong format return error
        else:
            return Parser.ERROR_OTHER
    

    def parse_instr_args(self, instr_sample):
        # Regex patterns for all types of arguments
        label_pattern = re.compile(r"^[a-zA-Z_$&%*!?-][\w\d_$&%*!?-]+$")
        var_pattern = re.compile(r"^(LF|TF|GF)@[a-zA-Z_$&%*!?-][\w\d_$&%*!?-]*")
        const_pattern = re.compile(r"^(bool|nil|int|string)@[\S]*")

        # Create new processed instruction class
        current_instr = ProcessedInstrunction(self.instr_num, instr_sample[0].upper(), len(self.process_line))
        current_instr.create_instr_line(self.xml_tree)

        # Iterate through all arguments and check if they are correct
        # Set every new argument into the processed instruction
        for word_num in range(1, len(instr_sample)):
        
            if not len(self.process_line):
                return Parser.ERROR_OTHER
            
            # If there is one operand left there might be a comment without space
            if len(instr_sample)-1 == word_num:
                temp_list = self.cut_comment(self.process_line[0])
                self.process_line.pop(0)
                self.process_line = temp_list + self.process_line
            
            if instr_sample[word_num] == "var":
                if (re.match(var_pattern, self.process_line[0])):
                    current_instr.arg_set(self.process_line[0], 'var')
                    self.process_line.pop(0)
                else:
                    return Parser.ERROR_OTHER
                
            elif instr_sample[word_num] == "symb":
                if (re.match(const_pattern, self.process_line[0])):
                    # Separetely check if the constant is correct in other method
                    check_func(self.parse_const(current_instr))           
                    self.process_line.pop(0)
                elif (re.match(var_pattern, self.process_line[0])):
                    current_instr.arg_set(self.process_line[0], 'var')
                    self.process_line.pop(0)
                else:
                    return Parser.ERROR_OTHER
                    
            elif instr_sample[word_num] == "label":
                if(re.match(label_pattern, self.process_line[0])):
                    current_instr.arg_set(self.process_line[0], 'label')
                    self.process_line.pop(0)
                else:
                    return Parser.ERROR_OTHER
                
            elif instr_sample[word_num] == "type":
                if (re.match("^(int|bool|string)$", self.process_line[0])):
                    current_instr.arg_set(self.process_line[0], 'type')
                    self.process_line.pop(0)
                else:
                    return Parser.ERROR_OTHER
            
                   
        return 0
                
    def get_next_line(self):
        # Read line and split it into list of words
        next_line = sys.stdin.readline()
       
        if next_line == "":
            return Parser.READING_END
        
        self.current_line = next_line.split()

        return 0
    
    @staticmethod
    def is_comment(string):
        # Comment test
        if re.match(r"^#", string):
            return True
        else:
            return False
            
    def parse_instr(self):
        # Iterate through all instructions and find the right one
        for inst in self.parser_instr_samples:
            if self.process_line[0].lower() == inst[0].lower():
                self.process_line.pop(0)
                check_func(self.parse_instr_args(inst))
                self.instr_num+=1
                return 0
        
        # Some instruction problems --> exit with error
        return Parser.ERROR_OPERATION_CODE

    def parse_line(self):
        # Save original current_line and change only process_line
        self.process_line = self.current_line

        # Based on header presence, set the state of parsing
        if self.read_header:
            self.parse_line_state = 1
        else:
            self.parse_line_state = 0
            # After header might be a comment without space
            if not self.is_comment(self.process_line[0]):
                tmp_list = self.cut_comment(self.process_line[0])
                self.process_line.pop(0)
                self.process_line = tmp_list + self.process_line
        
        # Line parsing working with FSM
        while len(self.process_line) > 0:
            if self.parse_line_state == 0:
                # <#> or <header>, other Error
                if self.is_comment(self.process_line[0]):
                    return 0
                elif self.process_line[0] == self.language_header:
                    self.process_line.pop(0)
                    self.read_header = True
                    self.parse_line_state = 1
                else:
                    return Parser.ERROR_MISSING_HEADER
                
            elif self.parse_line_state == 1:
                # <#> or <op-code>, other Error
                if self.is_comment(self.process_line[0]):
                    return 0
                if re.fullmatch(r"^[A-Za-z2]*$", self.process_line[0].lower()):
                    check_func(self.parse_instr())
                    self.parse_line_state = 2
                else:
                    return Parser.ERROR_OTHER
                
            elif self.parse_line_state == 2:
                # <#>, other Error
                if self.is_comment(self.process_line[0]):
                    return 0
                else:
                    return Parser.ERROR_OTHER
        
        return 0


def check_func(return_code):
    # Handle return codes from methods and function which can return error codes
    if return_code >= 10:
        print(f"ERROR: {return_code}")
        sys.exit(return_code)
    else:
        return return_code


def read_args(args):
    if (args[1] != '--help') or (args[1] == '--help' and len(args) > 2):
        return ERROR_INPUT_ARGS
    elif args[1] == '--help':
        print("\nA script of type filter (parse.py in Python 3.10) reads from the standard\n" 
        "input source code in IPP-code24, checks lexical and syntactic\n" 
        "the correctness of the code and prints the XML representation of the program to the standard output\n")
        sys.exit(0)


def main():
    # Read arguments
    args = sys.argv
    if len(args) > 1:
        if check_func(read_args(args)) is None:
            sys.exit(0)

    # Init parser for ippcode24
    ipp24_parser = Parser('IPPcode24', '.IPPcode24', False, "", 1, instruction_samples)

    # Create XML tree
    ipp24_parser.createXMLtree()

    # Read lines in loop and then if the line is not empty, parse it
    while check_func(ipp24_parser.get_next_line()) != Parser.READING_END:
        if len(ipp24_parser.current_line) > 0:
            check_func(ipp24_parser.parse_line())
   
    # Print XML after parsing
    ipp24_parser.printXMLtree()


if __name__ == "__main__":
    main()
