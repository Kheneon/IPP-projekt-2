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
#import atexit   

# Exit codes:
# 10 - missing parameter or forbiden combination of params
# 11 - open file failure
# 12 - file to write failure
# 
# 31 - XML file is not "well-formed"
# 32 - unexpected structure of XML
#
# 52 - redefinition of variable

#def exit_handler():
#    print("[DEBUG] exit debug write:")
#    print("[DEBUG]order_list:\n",Execution.instr_list.order_list)
#    print("[DEBUG]order_dict:\n",Execution.instr_list.order_dict)
#    print("[DEBUG]label_list:\n",Execution.instr_list.call_stack.label_list)
#atexit.register(exit_handler)



instr_index = 0

class ExecuteProgram():
    """
    Checks arguments\n
    Parses XML file\n
    """
    source_file = ""
    input_file = ""
    def __init__(self):
        global instr_index
        self.input_parameters(sys.argv)
        instr_list = InstructionList(self.source_file,self.input_file)
        stack = Stack()
        instr_list_length = len(instr_list.instruction_list)
        print("[DEBUG]order_list:\n",instr_list.order_list)
        print("[DEBUG]order_dict:\n",instr_list.order_dict)
        print("[DEBUG]label_list:\n",instr_list.call_stack.label_list)
        print("[DEBUG]label_order:\n",instr_list.call_stack.label_order)
        print("[DEBUG] executing:")
        while instr_index < instr_list_length:
            instruction = instr_list.instruction_list[instr_index]
            instr_list.instruction_check(instruction)
            instr_name = instruction.attrib.get('opcode').upper()
            print("INSTRUCTION:",instr_name,"\nindex:",instr_index)
            match instr_name:
                case "DEFVAR":
                    stack.defvar(instruction[0].text)
                case "CREATEFRAME":
                    stack.create_frame()
                case "PUSHFRAME":
                    stack.push_frame()
                case "POPFRAME":
                    stack.pop_frame()
                case "MOVE":
                    stack.move(instruction)
                case "CALL":
                    instr_list.call(instruction[0].text,instruction.attrib.get('order'))
                case "LABEL":
                    instr_index += 1
                    continue
                case "TYPE":
                    stack.to_type(instruction[0],instruction[1])
                case "PUSHS":
                    stack.pushs(instruction[0].attrib.get('type').upper(),instruction[0].text)
                case "POPS":
                    stack.pops(instruction[0].text)
                case "JUMP":
                    instr_list.jump(instruction[0].text,instruction.attrib.get('order'))
                case "RETURN":
                    instr_list.return_call()
                case "EXIT":
                    instr_list.exit_call(instruction[0].text)
                case "ADD"| "SUB" | "MUL" | "IDIV":
                    stack.calculation(instr_name,instruction[0].text,instruction[1].text,
                    instruction[1].attrib.get('type'),instruction[2].text,
                    instruction[2].attrib.get('type'))
                case "LT" | "GT" | "EQ":
                    stack.relation_operators(instr_name,instruction[0].text,instruction[1].text,
                    instruction[1].attrib.get('type'),instruction[2].text,
                    instruction[2].attrib.get('type'))
                case "AND" | "OR":
                    stack.bool_operators(instr_name,instruction[0].text,instruction[1].text,
                    instruction[1].attrib.get('type'),instruction[2].text,
                    instruction[2].attrib.get('type'))
                case "NOT":
                    stack.bool_operators(instr_name,instruction[0].text,instruction[1].text,
                    instruction[1].attrib.get('type'),None,None)

                case other:
                    exit(1)


            #print(instr_index)
            instr_index += 1



        #testing
        #stack.create_frame()
        
        #stack.push_frame()
        #stack.create_frame()
        #stack.push_frame()

        print("[DEBUG] State after execution:")
        stack.write_frames()
        instr_list.print_labels()
        stack.data_stack.write_data_stack()

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
        # instruction tag control
        counter = 1
        for arg in instruction:
            arg_name = "arg" + str(counter)
            if arg.tag != arg_name:
                print(arg_name,arg.text)
            counter += 1

        instr_name = instruction.attrib.get('opcode').upper()
        instr_arg_num = len(instruction)
        #no arguments
        if instr_name in ['CREATEFRAME','PUSHFRAME','POPFRAME','RETURN']:
            if instr_arg_num != 0:
                exit(1)
            return
        # arg1 = variable
        elif instr_name in ['DEFVAR','POPS']:
            if instr_arg_num != 1:
                exit(1) #TODO:errcode
            if instruction[0].attrib.get('type').upper() != "VAR":
                exit(1) #TODO:errcode
            return
        # arg1 = variable/const
        elif instr_name in ['PUSHS']:
            if instr_arg_num != 1:
                exit(1) #TODO:errcode
            if instruction[0].attrib.get('type').upper() not in ['VAR','INT','STRING','BOOL','NIL']:
                exit(1) #TODO:errcode
            return
        # arg1 = label
        elif instr_name in ['LABEL','CALL','JUMP']:
            if instr_arg_num != 1:
                exit(1) #TODO:errcode
            if instruction[0].attrib.get('type').upper() != "LABEL":
                exit(1) #TODO:errcode
            return
        # arg1 = INT
        elif instr_name in ['EXIT']:
            if instr_arg_num != 1:
                exit(1) #TODO:errcode
            if instruction[0].attrib.get('type').upper() != "INT":
                exit(1) #TODO:errcode
            return
        # arg1 = var, arg2 = const/var
        elif instr_name in ['MOVE','TYPE']:
            if instr_arg_num != 2:
                exit(1) #TODO: errcode
            if instruction[0].attrib.get('type').upper() != "VAR":
                exit(1) #TODO:errcode
            instr_name = instruction[1].attrib.get('type').upper()
            if instr_name not in ['VAR','INT','STRING','BOOL','NIL']:
                exit(1) #TODO:errcode
            return
        #arg1 = var, arg2 = var/int, arg3 = var/int
        elif instr_name in ['ADD','SUB','MUL','IDIV']:
            if instr_arg_num != 3:
                exit(1)
            if instruction[0].attrib.get('type').upper() != "VAR":
                exit(1) #TODO:errcode
            for i in range(instr_arg_num-1):
                instr_type = instruction[i+1].attrib.get('type').upper()
                if instr_type not in ['VAR','INT']:
                    exit(1) #TODO:errcode
            return
        #arg1 = var, arg2 = var/const, arg3 = var/const
        elif instr_name in ['LT','EQ','GT']:
            if instr_arg_num != 3:
                exit(1)
            if instruction[0].attrib.get('type').upper() != "VAR":
                exit(1) #TODO:errcode
            for i in range(instr_arg_num-1):
                instr_type = instruction[i+1].attrib.get('type').upper()
                if instr_type not in ['VAR','INT','BOOL','STRING','NIL']:
                    exit(1) #TODO:errcode
            return
        #arg1 = var, arg2 = var/bool, arg3 = var/bool
        elif instr_name in ['AND','OR']:
            if instr_arg_num != 3:
                exit(1)
            if instruction[0].attrib.get('type').upper() != "VAR":
                exit(1) #TODO:errcode
            for i in range(instr_arg_num-1):
                instr_type = instruction[i+1].attrib.get('type').upper()
                if instr_type not in ['BOOL','VAR']:
                    exit(1) #TODO:errcode
            return
        #arg1 = var, arg2 = var/bool
        elif instr_name in ['NOT']:
            if instr_arg_num != 2:
                exit(1)
            if instruction[0].attrib.get('type').upper() != "VAR":
                exit(1) #TODO:errcode
            if instruction[1].attrib.get('type').upper() not in ['VAR','BOOL']:
                exit(1) #TODO:errcode
            return
        else:
            exit(1) #TODO: errcode
        exit(1) #TODO: errcode

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
        name = self.stack.pop()
        self.stack_top -= 1
        return name

    def push(self,name):
        self.stack.append(name)
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
# INT2CHAR
# STRI2INT
# READ
# WRITE
# CONCAT
# STRLEN
# GETCHAR
# SETCHAR
# JUMPIFEQ
# JUMPIFNEQ
# DPRINT
# BREAK