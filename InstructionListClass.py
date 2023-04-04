from CallStackClass import *
import xml.etree.ElementTree as elemTree
import sys

class InstructionList:
    def __init__(self,source_file,input_file):
        self.source_file = source_file
        self.input_file = input_file
        self.instruction_list = []
        self.order_list = []
        self.order_dict = {}
        self.call_stack = CallStack()
        self.xml_parse()

    def xml_parse(self):
        """
        Function that controls if XML file is in good format.\n
        Returns Instructions class
        """
        if self.source_file == "":
            self.source_file = sys.stdin
        try:
            tree = elemTree.parse(self.source_file)
        except FileNotFoundError:
            exit(10)
        except:
            exit(31)

        root = tree.getroot()

        if root.tag != 'program':
            exit(31)

        language = root.attrib.get('language')
        if language != None:
            if language.upper() != 'IPPCODE23':
                exit(31)
        else:
            exit(31)

        for instruction in root:
            # each instruction has to have tag instruction
            if instruction.tag != 'instruction':
                exit(32)

            # each instruction has to have attribute order and it has to be integer > 0
            order = instruction.attrib.get('order')
            if order == None:
                exit(32)

            try:
                if int(order) < 1:
                    exit(32)
            except Exception:
                exit(32)

            # each instruction must contain attribute opcode
            if instruction.attrib.get('opcode') == None:
                exit(32)
            
            if order not in self.order_list:
                self.order_list.append(order)
            else:
                exit(32)

            if instruction.attrib.get('opcode') == "LABEL":
                if len(instruction) != 1:
                    exit(1) # Too many arguments 
                self.call_stack.add_label(instruction[0].text,instruction.attrib.get('order'))
            self.instruction_list.append(instruction)

        self.instruction_list = sorted(self.instruction_list, key=lambda instr: int(instr.attrib['order']))
        #self.order_list = [int(x) for x in self.order_list]
        self.order_list = sorted(self.order_list, key=lambda ord: int(ord))
        counter = 0
        for ord in self.order_list:
            self.order_dict[ord] = counter
            counter += 1


    def instruction_check(self,instruction):
        # instruction tag control (arg1,arg2,arg3)
        arg_num = len(instruction)
        arg_list = []
        for index in range(arg_num):
            arg_name = "arg"+str(index+1)
            arg_list.append(arg_name)

        for arg in instruction:
            if arg.tag not in arg_list:
                exit(1)
            arg_list.remove(arg.tag)

        instr_name = instruction.attrib.get('opcode').upper()
        instr_arg_num = len(instruction)
        param = [None] * instr_arg_num
        self.check_num_of_params(instr_name,instr_arg_num)
        for arg in instruction:
            param[int(arg.tag[3])-1] = arg.attrib.get('type')
        match instr_name:
            # no arguments
            case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK":
                return
            # arg1 = var
            case "DEFVAR" | "POPS":
                self.is_param_var(param[0])
            # arg1 = var/const
            case "PUSHS" | "WRITE" | "DPRINT":
                self.is_param_var_or_const(param[0])
            # arg1 = label
            case "LABEL" | "CALL" | "JUMP":
                self.is_param_label(param[0])
            # arg1 = int
            case "EXIT":
                self.is_param_int(param[0])
            # arg1 = var, arg2 = const/var
            case "MOVE" | "TYPE":
                self.is_param_var(param[0])
                self.is_param_var_or_const(param[1])
            # arg1 = var, arg2 = int/var
            case "INT2CHAR":
                self.is_param_var(param[0])
                self.is_param_var_or_int(param[1])
            # arg1 = var, arg2 = var/int, arg3 = var/int
            case "ADD" | "SUB" | "MUL" | "IDIV":
                self.is_param_var(param[0])
                self.is_param_var_or_int(param[1])
                self.is_param_var_or_int(param[2])
            # arg1 = var, arg2 = var/const, arg3 = var/const
            case "LT" | "GT" | "EQ":
                self.is_param_var(param[0])
                self.is_param_var_or_const(param[1])
                self.is_param_var_or_const(param[2])
            # arg1 = var, arg2 = var/bool, arg3 = var/bool
            case "AND" | "OR":
                self.is_param_var(param[0])
                self.is_param_var_or_bool(param[1])
                self.is_param_var_or_bool(param[2])
            # arg1 = var, arg2 = var/bool
            case "NOT":
                self.is_param_var(param[0])
                self.is_param_var_or_bool(param[1])
            # arg1 = var, arg2 = var/string, arg3 = var/int
            case "STRI2INT" | "GETCHAR":
                self.is_param_var(param[0])
                self.is_param_var_or_string(param[1])
                self.is_param_var_or_int(param[2])
            # arg1 = var, arg2 = type
            case "READ":
                self.is_param_var(param[0])
                self.is_param_type(param[1])
            # arg1 = var, arg2 = var/string, arg3 = var/string
            case "CONCAT":
                self.is_param_var(param[0])
                self.is_param_var_or_string(param[1])
                self.is_param_var_or_string(param[2])
            # arg1 = var, arg2 =  var/string
            case "STRLEN":
                self.is_param_var(param[0])
                self.is_param_var_or_string(param[1])
            # arg1 = var, arg2 = var/int, arg3 = var/string
            case "SETCHAR":
                self.is_param_var(param[0])
                self.is_param_var_or_int(param[1])
                self.is_param_var_or_string(param[2])
            case "JUMPIFEQ" | "JUMPIFNEQ":
                self.is_param_label(param[0])
                self.is_param_var_or_const(param[1])
                self.is_param_var_or_const(param[2])
            case other:
                exit(1)

    def check_num_of_params(self,name,value):
        """
        Function check if instruction has right ammount of parameters.\n
        Otherwise exits program
        """
        name_upper = name.upper()
        if value == 0:
            if name_upper not in ['CREATEFRAME','PUSHFRAME','POPFRAME','RETURN','BREAK']:
                exit(1)
        if value == 1:
            if name_upper not in ['DEFVAR','CALL','PUSHS','POPS','WRITE','LABEL','JUMP','EXIT','DPRINT']:
                exit(1)
        if value == 2:
            if name_upper not in ['MOVE','INT2CHAR','READ','STRLEN','TYPE','NOT']:
                exit(1)
        if value == 3:
            if name_upper not in ['ADD','SUB','MUL','IDIV','LT','GT','EQ','AND','OR','STRI2INT','CONCAT','GETCHAR','SETCHAR','JUMPIFEQ','JUMPIFNEQ']:
                exit(1)

    def is_param_var(self,type_to_check):
        if type_to_check.upper() != "VAR":
            exit(1)
    
    def is_param_int(self,type_to_check):
        if type_to_check.upper() != "INT":
            exit(1)

    def is_param_var_or_const(self,type_to_check):
        if type_to_check.upper() not in ['VAR','INT','BOOL','STRING','NIL']:
            exit(1)

    def is_param_label(self,type_to_check):
        if type_to_check.upper() != "LABEL":
            exit(1)

    def is_param_int(self,type_to_check):
        if type_to_check.upper() != "INT":
            exit(1)

    def is_param_var_or_int(self,type_to_check):
        if type_to_check.upper() not in ['VAR','INT']:
            exit(1)

    def is_param_var_or_bool(self,type_to_check):
        if type_to_check.upper() not in ['VAR','BOOL']:
            exit(1)

    def is_param_var_or_string(self,type_to_check):
        if type_to_check.upper() not in ['VAR','STRING']:
            exit(1)

    def is_param_type(self,type_to_check):
        if type_to_check.upper() not in ['TYPE']:
            exit(1)

    def call(self,name,order):
        global instr_index
        self.jump(name,order)
        self.call_stack.push(order)

    def jump(self,name,order):
        global instr_index
        if name not in self.call_stack.label_list:
            exit(1) #TODO:errcode
        instr_index = self.order_dict[self.call_stack.label_order[name]]
        print(instr_index)

    def return_call(self):
        global instr_index
        if self.call_stack.stack_top == -1:
            exit(1)
        print(self.call_stack.stack)
        name = self.call_stack.pop()
        instr_index = self.order_dict[name]
        print(instr_index)

    def exit_call(self,exit_code):
        try: int(exit_code)
        except ValueError:
            exit(57)
        exit(int(exit_code))
        

    def print_labels(self):
        print(self.call_stack.label_list)