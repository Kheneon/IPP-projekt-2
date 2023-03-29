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

        #testing
        frame_stack.create_frame()
        
        frame_stack.push_frame()
        frame_stack.create_frame()
        frame_stack.push_frame()

        frame_stack.write_frames()
        print(instr_list.instruction_list)

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
    instruction_list = []
    source_file = ""
    input_file = ""
    order_list = []
    def __init__(self,source_file,input_file):
        self.source_file = source_file
        self.input_file = input_file
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

            self.instruction_list.append(instruction)

class Frame:
    """
    Class just for creating frame\n
    Stores variables in dictionary
    """
    initialized = False
    variables = {}
    def __init__(self,initialize = False):
        self.initialized = initialize


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

    def write_frames(self):
        """Debug Output, shows actual state of frames and stack"""
        stack_size = len(self.stack) - 1
        print("[DEBUG] --- FrameStack ---")
        print("Frames on Stack: ", stack_size, "[Local frame is not included]")
        print("Local frame: ", self.local_frame.initialized)
        print("Temp Frame:  ", self.temp_frame.initialized)
        print("Global Frame: ", self.global_frame.initialized)

class CallStack:
    """Holds positions that we will return to"""
    def __init__(self):
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

# Executing program
Execution = ExecuteProgram()