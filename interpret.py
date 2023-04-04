#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   interpret.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
import re
import sys
import xml.etree.ElementTree as elemTree  

# Exit codes:
# 10 - missing parameter or forbiden combination of params
# 11 - open file failure
# 12 - file to write failure
# 
# 31 - XML file is not "well-formed"
# 32 - unexpected structure of XML
#
# 52 - redefinition of variable

instr_index = 0
file = None

class ExecuteProgram():
    """
    Checks arguments\n
    Parses XML file\n
    """
    source_file = ""
    input_file = ""
    def __init__(self):
        global instr_index
        global file
        self.input_parameters(sys.argv)
        instr_list = InstructionList(self.source_file,self.input_file)
        if self.input_file != "":
            file = open(self.input_file,"r")
        stack = Stack()
        instr_list_length = len(instr_list.instruction_list)
        # print("[DEBUG]order_list:\n",instr_list.order_list)
        # print("[DEBUG]order_dict:\n",instr_list.order_dict)
        # print("[DEBUG]label_list:\n",instr_list.call_stack.label_list)
        # print("[DEBUG]label_order:\n",instr_list.call_stack.label_order)
        # print("[DEBUG] executing:")
        exec_instr_counter = 0
        while instr_index < instr_list_length:
            exec_instr_counter += 1
            instruction = instr_list.instruction_list[instr_index]
            instr_list.instruction_check(instruction)
            instr_name = instruction.attrib.get('opcode').upper()
            print("INSTRUCTION:",instr_name,"\nindex:",instr_index)
            arg_name = [None] * len(instruction)
            arg_type = [None] * len(instruction)
            order = instruction.attrib.get('order')
            for arg in instruction:
                index = int(arg.tag[3])-1
                arg_name[index] = arg.text
                arg_type[index] = arg.attrib.get('type')
            match instr_name:
                case "DEFVAR":
                    stack.defvar(arg_name[0])
                case "CREATEFRAME":
                    stack.create_frame()
                case "PUSHFRAME":
                    stack.push_frame()
                case "POPFRAME":
                    stack.pop_frame()
                case "MOVE":
                    stack.move(instruction)
                case "CALL":
                    instr_list.call(arg_name[0],order)
                case "LABEL":
                    instr_index += 1
                    continue
                case "TYPE":
                    stack.to_type(instruction[0],instruction[1])
                case "PUSHS":
                    stack.pushs(instruction[0].attrib.get('type').upper(),arg_name[0])
                case "POPS":
                    stack.pops(arg_name[0])
                case "JUMP":
                    instr_list.jump(arg_name[0],order)
                case "RETURN":
                    instr_list.return_call()
                case "EXIT":
                    instr_list.exit_call(arg_name[0])
                case "ADD"| "SUB" | "MUL" | "IDIV":
                    stack.calculation(instr_name,arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case "LT" | "GT" | "EQ":
                    stack.relation_operators(instr_name,arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case "AND" | "OR":
                    stack.bool_operators(instr_name,arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case "NOT":
                    stack.bool_operators(instr_name,arg_name[0],arg_name[1],arg_type[1],None,None)
                case "WRITE":
                    stack.write(arg_name[0],arg_type[0])
                case "BREAK":
                    stack.break_instr(order,exec_instr_counter)
                case "DPRINT":
                    stack.write(arg_name[0],arg_type[0],output=sys.stderr)
                case "INT2CHAR":
                    stack.int2char(arg_name[0],arg_type[0],arg_name[1],arg_type[1])
                case "STRI2INT":
                    stack.stri2int(arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case "READ":
                    stack.read(arg_name[0],arg_name[1])
                case "CONCAT":
                    stack.concat(arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case "STRLEN":
                    stack.strlen(arg_name[0],arg_name[1],arg_type[1])
                case "GETCHAR":
                    stack.getchar(arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case "SETCHAR":
                    stack.setchar(arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2])
                case other:
                    exit(1)

            instr_index += 1
        if file != None:
            file.close()


        #testing
        #stack.create_frame()
        
        #stack.push_frame()
        #stack.create_frame()
        #stack.push_frame()

        #print("[DEBUG] State after execution:")
        #stack.write_frames()
        #instr_list.print_labels()
        #stack.data_stack.write_data_stack()

    def input_parameters(self,argv):
        """
        Function that controls parameters from command line
        """
        argc = len(argv)
        if argc < 2 or argc > 3:
            exit(10)
        if argv[1] == "--help" and argc < 3:
            print("HELP") #TODO: Help
            exit(0)
        for argument in argv[1:]:
            if argument[0:8] == "--input=":
                if self.input_file != "":
                    exit(10)
                self.input_file = argument[8:]
                if self.input_file == "":
                    exit(10)
            elif argument[0:9] == "--source=":
                if self.source_file != "":
                    exit(10)
                self.source_file = argument[9:]
                if self.source_file == "":
                    exit(10)
            else:
                exit(10)


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

class Variable:
    def __init__(self,name):
        self.name = name
        self.var_type = "none"
        self.value = None

    def assign(self,value,var_type):
        self.value = value
        self.var_type = var_type

class Frame:
    """
    Class just for creating frame\n
    Stores variables in dictionary
    """
    def __init__(self,initialize = False):
        self.initialized = initialize
        self.variables = []
        self.var_list = []

    def defvar(self,name):
        if name == "":
            exit(1) #TODO: errcode
        if name in self.var_list:
            exit(52)
        self.variables.append(Variable(name))
        self.var_list.append(name)

    def write_var(self):
        for var in self.variables:
            print("\t[name]",var.name,"[type]",var.var_type,"[value]",var.value)

class FrameStack:
    def __init__(self):
        self.global_frame = Frame(True) #Global
        self.local_frame = Frame(False) #Local
        self.temp_frame = Frame(False)  #Temporary
        self.stack = []                 #Empty stack
        self.stack_top = -1

class Stack:
    """
    Stacks\n
    Includes Frame Stack
    Includes Data Stack
    Includes Call Stack
    """
    def __init__(self):
        self.frame_stack = FrameStack()
        self.data_stack = DataStack()
        self.call_stack = CallStack()

    def create_frame(self):
        """Creating temporary frame"""
        self.frame_stack.temp_frame = Frame(True)
        #print("create frame")

    def pop_frame(self):
        """Pops Local frame to Temporary frame, remove previous Temporary frame"""
        if self.stack_top == -1:
            exit(55) # no frame to pop from stack left

        self.frame_stack.temp_frame = self.frame_stack.local_frame
        self.frame_stack.local_frame = self.stack[self.stack_top] 
        self.stack_top -= 1
        self.stack.pop()
        #print("pop frame")

    def push_frame(self):
        """
        Pushing Temporary Frame on Stack, now it is Local frame
        """
        if self.frame_stack.temp_frame.initialized == False:
            exit(55) # Pushing uninitialized frame

        self.stack.append(self.local_frame)
        self.stack_top += 1
        self.frame_stack.local_frame = self.temp_frame
        self.frame_stack.temp_frame = Frame(False)
        #print("pushing frame")

    def defvar(self,name):
        if name[0:3] == "GF@":
            self.frame_stack.global_frame.defvar(name[3:])
        elif name[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == True:
                self.frame_stack.local_frame.defvar(name[3:])
            else:
                exit(1) #defvarr on uninitialized frame TODO: error code
        elif name[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == True:
                self.frame_stack.temp_frame.defvar(name[3:])
            else:
                exit(1) #defvar on uninitialized frameTODO: err code
        else:
            exit(1) #defvar not with variable with LF/TF/GF TODO: errcode

    def move(self,instruction):
        """Function represents MOVE instruction"""
        arg1 = instruction[0].text[3:]
        if self.is_initialized(instruction[0].text) == False:
            exit(1) #TODO: errcode
        if instruction[1].attrib.get('type').upper() == 'VAR':
            if self.is_assigned(instruction[0].text) == False:
                exit(1) #TODO: errcode
            new_type,new_value = self.get_type_and_value(instruction[1].text)
        else: # int, string, bool, nil
            new_type = instruction[1].attrib.get('type').upper()
            if new_type not in ['STRING','BOOL','NIL','INT']:
                exit(1) #TODO: errcode
            new_value = instruction[1].text
        self.assign(instruction[0].text,new_value,new_type)

    def to_type(self,dest,src):
        """
        Function takes on input
        @param: dest Name of variable. Where to save result of operation
        @param: src  Scans this variable and constant, type saves into dest
        """
        if self.is_initialized(dest.text) == False:
            exit(1)
        src_type = src.attrib.get('type').upper()
        if src_type == 'VAR':
            if self.is_assigned(src.text) == False:
                exit(1) #TODO: errcode
            new_value,_ = self.get_type_and_value(src.text)
            new_type = "STRING"
            self.assign(dest.text,new_value,new_type)
        elif src_type in ['INT','STRING','BOOL','NIL']:
            self.assign(dest.text,src_type.lower(),"STRING")

    def is_initialized(self,name):
        """Function checks if variable is initialized"""
        var_list = []
        if name[0:3] == "GF@":
            var_list = self.frame_stack.global_frame.var_list
        if name[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            var_list = self.frame_stack.local_frame.var_list
        if name[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            var_list = self.frame_stack.temp_frame.var_list
        if name[3:] not in var_list:
            return False
        return True

    def assign(self,name,new_value,new_type):
        if name[0:3] == "GF@":
            for var in self.frame_stack.global_frame.variables:
                if var.name == name[3:]:
                    var.assign(new_value,new_type)
        if name[0:3] == "LF@":
            for var in self.frame_stack.local_frame.variables:
                if var.name == name[3:]:
                    var.assign(new_value,new_type)
        if name[0:3] == "TF@":
            for var in self.frame_stack.temp_frame.variables:
                if var.name == name[3:]:
                    var.assign(new_value,new_type)

    def get_type_and_value(self,name):
        """
        Function returns Type and Value of variable
        Exits program if frames are not initialized
        Exits program if variable is uninitialized
        """
        if self.is_assigned(name) == False:
            exit(1)
        if name[0:3] == "GF@":
            variables = self.frame_stack.global_frame.variables
        if name[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            variables = self.frame_stack.local_frame.variables
        if name[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            variables = self.frame_stack.temp_frame.variables
        for var in variables:
            if name[3:] == var.name:
                return var.var_type,var.value

    def is_assigned(self,name):
        #print(name[3:])
        if self.is_initialized(name) == False:
            exit(1) #TODO: errcode
        if name[0:3] == "GF@":
            frame = self.frame_stack.global_frame
        if name[0:3] == "LF@":
            frame = self.frame_stack.local_frame
        if name[0:3] == "TF@":
            frame = self.frame_stack.temp_frame
        for var in frame.variables:
            if var.name == name[3:]:
                if var.var_type != None:
                    return True
        return False


    def write_frames(self):
        """Debug Output, shows actual state of frames and stack"""
        stack_size = len(self.frame_stack.stack) - 1
        print("[DEBUG] --- FrameStack ---")
        print("Frames on Stack: ", stack_size, "[Local frame is not included]")
        print("Local frame: ", self.frame_stack.local_frame.initialized)
        self.frame_stack.local_frame.write_var()
        print("Temp Frame:  ", self.frame_stack.temp_frame.initialized)
        self.frame_stack.temp_frame.write_var()
        print("Global Frame: ", self.frame_stack.global_frame.initialized)
        self.frame_stack.global_frame.write_var()

    def pushs(self,var_type,value):
        if var_type == "VAR":
            if self.is_assigned(value) == False:
                exit(1) #TODO: errcode
            new_type,new_value = self.get_type_and_value(value)
        elif var_type in ['STRING','BOOL','INT','NIL']:
            new_type = var_type.upper()
            new_value = value
        self.data_stack.push(new_value,new_type)

    def pops(self,var_name):
        if self.is_initialized(var_name) == False:
            exit(1) #TODO: errcode
        var_to_save = self.data_stack.stack.pop()
        self.assign(var_name,var_to_save.value,var_to_save.var_type)

    def calculation(self,type_of_calc,dest,src1,src1_type,src2,src2_type):
        """
        Function that provides calculation instructions [ADD,SUB,MUL,IDIV]\n
        Exits program if:
        - @param dest is not initalized
        - @param src1 or src2 has bad type or has uninitalized values
        """
        if self.is_initialized(dest) == False:
            exit(1)
        if src1_type.upper() in ['VAR']:
            src1_type,src1_value = self.get_type_and_value(src1)
        else:
            src1_value = src1
        if src1_value.isdigit() == False:
            exit(1) #TODO:errcode
    
        if src1_type.upper() not in ['INT']:
            exit(1) #TODO:errcode 52
        if src2_type.upper() in ['VAR']:
            src2_type,src2_value = self.get_type_and_value(src2)
        else:
            src2_value = src2
        if src2_type.upper() not in ['INT']:
            exit(1) #TODO:errcode 52
        if src1_value.isdigit() == False:
            exit(2) #TODO:errcode
        match type_of_calc.upper():
            case 'ADD':
                dest_value = int(src1_value) + int(src2_value)
            case 'SUB':
                dest_value = int(src1_value) - int(src2_value)
            case 'MUL':
                dest_value = int(src1_value) * int(src2_value)
            case 'IDIV':
                dest_value = int(int(src1_value) / int(src2_value))
            case other:
                exit(1)
        self.assign(dest,dest_value,'INT')
            
    def relation_operators(self,type_of_oper,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1)

        if src1_type.upper() in ['VAR']:
            src1_type,src1_value = self.get_type_and_value(src1)
        else:
            src1_value = src1
        if src1_type.upper() not in ['INT','BOOL','STRING','NIL']:
            exit(52) #TODO:errcode 52
        
        if src2_type.upper() in ['VAR']:
            src2_type,src2_value = self.get_type_and_value(src2)
        else:
            src2_value = src2
        if src2_type.upper() not in ['INT','BOOL','STRING','NIL']:
            exit(52) #TODO:errcode 52
        
        new_value = "false"
        new_type = "BOOL"
        if src1_type != src2_type:
            if type_of_oper.upper() == 'EQ':
                if src1_type.upper() == "NIL" or src2_type.upper() == "NIL":
                    self.assign(dest,new_value,new_type)
                else:
                    exit(1) #TODO:errcode
            else:
                exit(1) #TODO:errcode

        match type_of_oper.upper():
            case "EQ":
                if src1_value == src2_value:
                    new_value = "true"
            case "LT":
                if src1_value < src2_value:
                    new_value = "true"
            case "GT":
                if src1_value > src2_value:
                    new_value = "true"
            case other:
                exit(1) #TODO:errcode unknown instruction
        self.assign(dest,new_value,new_type)

    def bool_operators(self,type_of_oper,dest,src1,src1_type,src2,src2_type):
        new_value = "false"
        new_type = "BOOL"
        if self.is_initialized(dest) == False:
            exit(1)

        if src1_type.upper() in ['VAR']:
            src1_type,src1_value = self.get_type_and_value(src1)
        else:
            src1_value = src1
        if src1_type.upper() not in ['BOOL']:
            exit(52) #TODO:errcode 52
        
        if type_of_oper.upper() != "NOT":
            if src2_type.upper() in ['VAR']:
                src2_type,src2_value = self.get_type_and_value(src2)
            else:
                src2_value = src2
            if src2_type.upper() not in ['BOOL']:
                exit(52) #TODO:errcode 52
        else:
            if src1_value == "true":
                self.assign(dest,"false","BOOL")
            else:
                self.assign(dest,"true","BOOL")
            return

        match type_of_oper.upper():
            case "AND":
                if src1_value == src2_value:
                    new_value = "true"
            case "OR":
                if src1_value != "false" or src2_value != "false":
                    new_value = "true"
                    
            case other:
                exit(1) #TODO:errcode unknown instruction
        self.assign(dest,new_value,new_type)

    def write(self,to_write,to_write_type,output=sys.stdout):
        if to_write_type.upper() == "VAR":
            new_type,new_value = self.get_type_and_value(to_write)
        else:
            new_type = to_write_type.upper()
            new_value = to_write
        # print(new_type,new_value)
        match new_type:
            case "INT":
                print(new_value,end='',file=output)
            case "BOOL":
                if new_value == "true":
                    print("true",end='',file=output)
                else:
                    print("false",end='',file=output)
            case "NIL":
                print("",end='')
            case "STRING":
                substrings = self.remove_escape_sequence(new_value)
                if substrings == None: # String without escape sequences
                    return
                for substr in substrings:
                    print(substr,end='',file=output)
            case other:
                exit(1)

    def remove_escape_sequence(self,string_to_modify):
        """
        Function removes escape sequences
        @return: List of strings without escape sequences
        """
        buffer = string_to_modify.split("\\")
        if len(buffer) == 1:
            return buffer
        new_buffer = []
        new_buffer.append(buffer[0])
        for substring in buffer[1:]:
            new_char = chr(int(substring[0:3]))
            new_substring = substring.replace(substring[0:3],new_char,1)
            new_buffer.append(new_substring)
        return new_buffer

    def break_instr(self,order,num_of_exec_instr):
        print("CONTROL OUTPUT:",file=sys.stderr)
        print("\tOrder of instruction: ",int(order),file=sys.stderr)
        print("\tExecuted instructions: ",num_of_exec_instr," (actual instruction included)",file=sys.stderr)
        print("\tTemporary Frame\t[initialized:",self.frame_stack.temp_frame.initialized,"]:",file=sys.stderr)
        for var in self.frame_stack.temp_frame.variables:
            print("\t\t[name] ",var.name,"\t[type] ",var.var_type,"\t[value] ",var.value,file=sys.stderr)
        print("\tLocal Frame\t[initialized: ",self.frame_stack.local_frame.initialized,"]:",file=sys.stderr)
        for var in self.frame_stack.local_frame.variables:
            print("\t\t[name] ",var.name,"\t[type] ",var.var_type,"\t[value] ",var.value,file=sys.stderr)
        print("\tGlobal Frame:",file=sys.stderr)
        for var in self.frame_stack.global_frame.variables:
            print("\t\t[name] ",var.name,"\t[type] ",var.var_type,"\t[value] ",var.value,file=sys.stderr)

    def int2char(self,dest,dest_type,src,src_type):
        if src_type.upper() == "VAR":
            new_type, new_value = self.get_type_and_value(src)
        else:
            new_type = src_type
            new_value = src
        try: new_value = chr(int(new_value))
        except ValueError: exit(4) #TODO:errcode
        except OverflowError: exit(5) #TODO:errcode
        if self.is_initialized(dest) == False:
            exit(1) #TODO:errcode
        self.assign(dest,new_value,new_type.upper())

    def stri2int(self,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1) #TODO:errcode
        if src1_type == "VAR":
            src1_new_type, src1_new_value = self.get_type_and_value(src1)
        else:
            src1_new_type = src1_type
            src1_new_value = src1
        if src2_type == "VAR":
            src2_new_type, src2_new_value = self.get_type_and_value(src2)
        else:
            src2_new_type = src2_type
            src2_new_value = src2
        src1_len = len(src1_new_value)
        print(src1_len)
        if src1_len <= int(src2_new_value):
            exit(1)
        dest_value = ord(src1_new_value[int(src2_new_value)])
        self.assign(dest,dest_value,"INT")

    def read(self,dest,read_type):
        global file
        if file == None: #reading from stdin
            line = sys.stdin.readline()
        else: #reading from file
            line = file.readline()
        new_type = read_type.upper()
        if not line:
            value = "nil"
            new_type = "NIL"
        else:
            match read_type.upper():
                case "INT":
                    try: value = int(line)
                    except ValueError:
                        value = "nil"
                        new_type = "NIL"
                case "STRING":
                    value = line
                case "BOOL":
                    if line == "true":
                        value = "true"
                    else:
                        value = "false"

                case other:
                    exit(1)
        self.assign(dest,value,new_type.upper())

    def concat(self,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1)
        
        if src1_type.upper() == "VAR":
            new_src1_type, new_src1_val = self.get_type_and_value(src1)
        else:
            new_src1_type = src1_type
            new_src1_val = src1
        if new_src1_type.upper() != "STRING":
            exit(1)

        if src2_type.upper() == "VAR":
            new_src2_type, new_src2_val = self.get_type_and_value(src2)
        else:
            new_src2_type = src2_type
            new_src2_val = src2
        if new_src2_type.upper() != "STRING":
            exit(1)

        dest_value = new_src1_val + new_src2_val
        self.assign(dest,dest_value,"STRING")

    def strlen(self,dest,src1,src1_type):
        if self.is_initialized(dest) == False:
            exit(1)

        if src1_type.upper() == "VAR":
            new_src1_type, new_src1_val = self.get_type_and_value(src1)
        else:
            new_src1_type = src1_type
            new_src1_val = src1
        if new_src1_type.upper() != "STRING":
            exit(1)

        dest_value = len(new_src1_val)
        self.assign(dest,dest_value,"INT")
        
    def getchar(self,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1)
        
        if src1_type.upper() == "VAR":
            new_src1_type, new_src1_val = self.get_type_and_value(src1)
        else:
            new_src1_type = src1_type
            new_src1_val = src1
        if new_src1_type.upper() != "STRING":
            exit(1)

        if src2_type.upper() == "VAR":
            new_src2_type, new_src2_val = self.get_type_and_value(src2)
        else:
            new_src2_type = src2_type
            new_src2_val = src2
        if new_src2_type.upper() != "INT":
            exit(1)

        new_src1_len = len(new_src1_val)
        if new_src1_len <= int(new_src2_val):
            exit(58)
        dest_value = new_src1_val[int(new_src2_val)]
        self.assign(dest,dest_value,"STRING")

    def setchar(self,dest,src1,src1_type,src2,src2_type):
        new_dest_type, new_dest_val = self.get_type_and_value(dest)
        if new_dest_type.upper() != "STRING":
            exit(1)

        if src1_type.upper() == "VAR":
            new_src1_type, new_src1_val = self.get_type_and_value(src1)
        else:
            new_src1_type = src1_type
            new_src1_val = src1
        if new_src1_type.upper() != "INT":
            exit(1)

        if src2_type.upper() == "VAR":
            new_src2_type, new_src2_val = self.get_type_and_value(src2)
        else:
            new_src2_type = src2_type
            new_src2_val = src2
        if new_src2_type.upper() != "STRING":
            exit(1)

        new_src2_len = len(new_src2_val)
        if not new_src2_len:
            exit(58)
        new_dest_len = len(new_dest_val)
        if new_dest_len <= int(new_src1_val):
            exit(58)
        print(new_dest_val)
        new_dest_val = new_dest_val[:int(new_src1_val)] + new_src2_val[0] + new_dest_val[int(new_src1_val)+1:]
        self.assign(dest,new_dest_val,"STRING")

class CallStack:
    """Holds positions that we will return to"""
    def __init__(self):
        self.label_order = {}
        self.label_list = []
        self.stack = []
        self.stack_top = -1
    
    def pop(self):
        if self.stack_top == -1:
            exit(1) # Call stack is empty TODO: exit code
        order = self.stack.pop()
        self.stack_top -= 1
        return order

    def push(self,order):
        self.stack.append(order)
        self.stack_top += 1
    
    def add_label(self,name,order):
        self.label_order[name] = order
        self.label_list.append(name)

class DataStack:
    def __init__(self):
        self.stack = []
    
    def pop(self):
        return self.stack.pop()

    def push(self,value,var_type):
        var = Variable(None)
        var.assign(value,var_type)
        self.stack.append(var)

    def write_data_stack(self):
        print("[DEBUG] --- DATA STACK ---\n[TOP]")
        for var in self.stack:
            print("[TYPE] ",var.var_type," [VALUE] ",var.value)
        print("[BOTTOM]")

# Executing program
Execution = ExecuteProgram()

#TODO:
# SETCHAR
# JUMPIFEQ
# JUMPIFNEQ