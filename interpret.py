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

from VariableClass import *
from CallStackClass import *
from StackClass import *
from InstructionListClass import *

class ExecuteProgram():
    """
    Checks arguments\n
    Parses XML file\n
    Runs program
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
                    stack.to_type(arg_name[0],arg_name[1],arg_name[1])
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
                case "JUMPIFEQ":
                    stack.jumpifeq(arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2],instr_list.call_stack,instr_list.order_dict)
                case "JUMPIFNEQ":
                    stack.jumpifeq(arg_name[0],arg_name[1],arg_type[1],arg_name[2],arg_type[2],instr_list.call_stack,instr_list.order_dict,neq=True)
                case other:
                    exit(1)

            instr_index += 1
        if file != None:
            file.close()

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

# Executing program
Execution = ExecuteProgram()

#TODO: