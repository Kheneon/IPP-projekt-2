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
        frame_stack = FrameStack()
        for instruction in instr_list.instruction_list:
            instr_list.instruction_check(instruction)
            instr_name = instruction.attrib.get('opcode').upper()
            if instr_name == "DEFVAR":
                frame_stack.defvar(instruction[0].text)
            elif instr_name == "CREATEFRAME":
                frame_stack.create_frame()
            elif instr_name == "PUSHFRAME":
                frame_stack.push_frame()
            elif instr_name == "POPFRAME":
                frame_stack.pop_frame()
            elif instr_name == "MOVE":
                frame_stack.move(instruction)
            elif instr_name == "CALL":
                instr_list.call(instruction)
            elif instr_name == "LABEL":
                continue
            


        #testing
        #frame_stack.create_frame()
        
        #frame_stack.push_frame()
        #frame_stack.create_frame()
        #frame_stack.push_frame()

        frame_stack.write_frames()
        print(instr_list.instruction_list)
        instr_list.print_labels()

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
        elif instr_name in ['DEFVAR']:
            if instr_arg_num != 1:
                exit(1) #TODO:errcode
            if instruction[0].attrib.get('type').upper() != "VAR":
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
        elif instr_name in ['MOVE']:
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
    """
    Stack for frames\n
    Includes Temporary, Local and Global Frame
    """
    def __init__(self):
        self.global_frame = Frame(True) #Global
        self.local_frame = Frame(False) #Local
        self.temp_frame = Frame(False)  #Temporary
        self.stack = []                 #Empty stack
        self.stack_top = -1

    def create_frame(self):
        """Creating temporary frame"""
        self.temp_frame.initialized = True
        print("create frame")

    def pop_frame(self):
        """Pops Local frame to Temporary frame, remove previous Temporary frame"""
        if self.stack_top == -1:
            exit(55) # no frame to pop from stack left

        self.temp_frame = self.local_frame
        self.local_frame = self.stack[self.stack_top] 
        self.stack_top -= 1
        self.stack.pop()
        print("pop frame")

    def push_frame(self):
        """
        Pushing Temporary Frame on Stack, now it is Local frame
        """
        if self.temp_frame.initialized == False:
            exit(55) # Pushing uninitialized frame

        self.stack.append(self.local_frame)
        self.stack_top += 1
        self.local_frame = self.temp_frame
        self.temp_frame = Frame(False)
        print("pushing frame")

    def defvar(self,name):
        if name[0:3] == "GF@":
            self.global_frame.defvar(name[3:])
        elif name[0:3] == "LF@":
            if self.local_frame.initialized == True:
                self.local_frame.defvar(name[3:])
            else:
                exit(1) #defvarr on uninitialized frame TODO: error code
        elif name[0:3] == "TF@":
            if self.temp_frame.initialized == True:
                self.temp_frame.defvar(name[3:])
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

    def is_initialized(self,name):
        """Function checks if variable is initialized"""
        if name[0:3] == "GF@":
            var_list = self.global_frame.var_list
        if name[0:3] == "LF@":
            if self.local_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            var_list = self.local_frame.var_list
        if name[0:3] == "TF@":
            if self.temp_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            var_list = self.temp_frame.var_list
        if name[3:] not in var_list:
            return False
        return True

    def assign(self,name,new_value,new_type):
        if name[0:3] == "GF@":
            for var in self.global_frame.variables:
                if var.name == name[3:]:
                    var.assign(new_value,new_type)
        if name[0:3] == "LF@":
            for var in self.local_frame.variables:
                if var.name == name[3:]:
                    var.assign(new_value,new_type)
        if name[0:3] == "TF@":
            for var in self.temp_frame.variables:
                if var.name == name[3:]:
                    var.assign(new_value,new_type)

    def get_type_and_value(self,name):
        """Function returns Value and Type of variable"""
        if name[0:3] == "GF@":
            variables = self.global_frame.variables
        if name[0:3] == "LF@":
            if self.local_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            variables = self.local_frame.variables
        if name[0:3] == "TF@":
            if self.temp_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            variables = self.temp_frame.variables
        for var in variables:
            if name[3:] == var.name:
                return var.type,var.value

    def is_assigned(self,name):
        if self.is_initialized(name) == False:
            exit(1) #TODO: errcode
        if name[0:3] == "GF@":
            frame = self.global_frame
        if name[0:3] == "LF@":
            frame = self.local_frame
        if name[0:3] == "TF@":
            frame = self.temp_frame
        for var in frame.variables:
            if var.name == name:
                if var.type != None:
                    return True
        return False


    def write_frames(self):
        """Debug Output, shows actual state of frames and stack"""
        stack_size = len(self.stack) - 1
        print("[DEBUG] --- FrameStack ---")
        print("Frames on Stack: ", stack_size, "[Local frame is not included]")
        print("Local frame: ", self.local_frame.initialized)
        self.local_frame.write_var()
        print("Temp Frame:  ", self.temp_frame.initialized)
        self.temp_frame.write_var()
        print("Global Frame: ", self.global_frame.initialized)
        self.global_frame.write_var()

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
# TYPE
# LABEL
# JUMP
# JUMPIFEQ
# JUMPIFNEQ
# EXIT
# DPRINT
# BREAK