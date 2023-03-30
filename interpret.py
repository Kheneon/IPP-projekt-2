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
class ExecuteProgram():
    """
    Checks arguments\n
    Parses XML file\n
    """
    source_file = ""
    input_file = ""
    def __init__(self):
        self.input_parameters(sys.argv)
        instr_list = InstructionList(self.source_file,self.input_file)
        stack = Stack()
        for instruction in instr_list.instruction_list:
            instr_list.instruction_check(instruction)
            instr_name = instruction.attrib.get('opcode').upper()
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
                    instr_list.call(instruction)
                case "LABEL":
                    continue
                case "TYPE":
                    stack.to_type(instruction[0],instruction[1])
                case "PUSHS":
                    stack.pushs(instruction[0].attrib.get('type').upper(),instruction[0].text)
                case "POPS":
                    stack.pops(instruction[0].text)



        #testing
        #stack.create_frame()
        
        #stack.push_frame()
        #stack.create_frame()
        #stack.push_frame()

        stack.write_frames()
        print(instr_list.instruction_list)
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
        print(instr_name,instr_arg_num)
        #no arguments
        if instr_name in ['CREATEFRAME','PUSHFRAME','POPFRAME']:
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
        elif instr_name in ['LABEL']:
            if instr_arg_num != 1:
                exit(1) #TODO:errcode
            if instruction[0].attrib.get('type').upper() != "LABEL":
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
                if instr_type != "VAR" and instr_type != "INT":
                    exit(1) #TODO:errcode
            return
        
        else:
            exit(1) #TODO: errcode
        exit(1) #TODO: errcode

    def call(self):
        self.call_stack.push()

    def print_labels(self):
        print(self.call_stack.labels)

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
        self.frame_stack.temp_frame.initialized = True
        print("create frame")

    def pop_frame(self):
        """Pops Local frame to Temporary frame, remove previous Temporary frame"""
        if self.stack_top == -1:
            exit(55) # no frame to pop from stack left

        self.frame_stack.temp_frame = self.frame_stack.local_frame
        self.frame_stack.local_frame = self.stack[self.stack_top] 
        self.stack_top -= 1
        self.stack.pop()
        print("pop frame")

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
        print("pushing frame")

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
        """Function returns Value and Type of variable"""
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
        print(name[3:])
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

class CallStack:
    """Holds positions that we will return to"""
    def __init__(self):
        self.labels = {}
        self.stack = []
        self.stack_top = -1
    
    def pop(self):
        if self.stack_top == -1:
            exit(1) # Call stack is empty TODO: exit code
        self.stack.pop()
        self.stack_top -= 1

    def push(self,number):
        self.stack.append(int(number))
        self.stack_top += 1
    
    def add_label(self,name,order):
        self.labels[name] = order

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
# CALL
# RETURN
# PUSHS
# POPS
# ADD
# SUB
# MUL
# IDIV
# LT, GT, EQ
# AND, OR, NOT
# INT2CHAR
# STRI2INT
# READ
# WRITE
# CONCAT
# STRLEN
# GETCHAR
# SETCHAR
# JUMP
# JUMPIFEQ
# JUMPIFNEQ
# EXIT
# DPRINT
# BREAK