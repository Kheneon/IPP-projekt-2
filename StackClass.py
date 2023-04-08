#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   StackClass.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
from FrameStackClass import *
from DataStackClass import *
import sys

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
        self.file = None

    def create_frame(self):
        self.frame_stack.create_frame()

    def pop_frame(self):
        self.frame_stack.pop_frame()

    def push_frame(self):
        self.frame_stack.push_frame()

    def defvar(self,name):
        if name[0:3] == "GF@":
            self.frame_stack.global_frame.defvar(name[3:])
        elif name[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == True:
                self.frame_stack.local_frame.defvar(name[3:])
            else:
                exit(55) #defvarr on uninitialized frame
        elif name[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == True:
                self.frame_stack.temp_frame.defvar(name[3:])
            else:
                exit(55) #defvar on uninitialized frame
        else:
            exit(52) #defvar not with variable with LF/TF/GF #TODO:errcode

    def move(self,dest,src,src_type):
        """Function represents MOVE instruction"""
        self.is_initialized(dest)
        new_type,new_value = self.get_type_and_value(src,src_type)
        self.assign(dest,new_value,new_type)

    def to_type(self,dest,src,src_type):
        """
        Function takes on input
        @param: dest Name of variable. Where to save result of operation
        @param: src  Scans this variable and constant, type saves into dest
        """
        # print(self.frame_stack.global_frame.var_list)
        self.is_initialized(dest)
        if src_type.upper() == "VAR" and not self.is_assigned(src):
            self.assign(dest,"","STRING")
            return
        new_value,new_type = self.get_type_and_value(src,src_type)
        new_type = "STRING"
        self.assign(dest,new_value.lower(),new_type)

    def is_initialized(self,name):
        """Function checks if variable is initialized"""
        var_list = []
        if name[0:3] == "GF@":
            var_list = self.frame_stack.global_frame.var_list
        elif name[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == False:
                exit(55) #uninitalized frame
            var_list = self.frame_stack.local_frame.var_list
        elif name[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == False:
                exit(55) #uninitalized frame
            var_list = self.frame_stack.temp_frame.var_list
        if name[3:] not in var_list:
            exit(54)

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

    def get_type_and_value(self,variable,variable_type):
        """
        Function returns Type and Value of variable\n
        If it is not variable, but constant, returns constant\n
        Exits program if frames are not initialized\n
        Exits program if variable is uninitialized
        """
        if variable_type.upper() != "VAR":
            return variable_type,variable
        if not self.is_assigned(variable):
            exit(56) # variable has no value
        if variable[0:3] == "GF@":
            variables = self.frame_stack.global_frame.variables
        elif variable[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == False:
                exit(55) #uninitalized frame
            variables = self.frame_stack.local_frame.variables
        elif variable[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == False:
                exit(55) #uninitalized frame
            variables = self.frame_stack.temp_frame.variables
        for var in variables:
            if variable[3:] == var.name:
                return var.var_type,var.value

    def is_assigned(self,name):
        self.is_initialized(name)
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
        new_type,new_value = self.get_type_and_value(value,var_type)
        new_type = var_type.upper()
        new_value = value
        self.data_stack.push(new_value,new_type)

    def pops(self,var_name):
        self.is_initialized(var_name)
        var_to_save = self.data_stack.pop()
        self.assign(var_name,var_to_save.value,var_to_save.var_type)

    def calculation(self,type_of_calc,dest,src1,src1_type,src2,src2_type):
        """
        Function that provides calculation instructions [ADD,SUB,MUL,IDIV]\n
        Exits program if:
        - @param dest is not initalized
        - @param src1 or src2 has bad type or has uninitalized values
        """
        self.is_initialized(dest)
        new_src1_type,new_src1_value = self.get_type_and_value(src1,src1_type)
        self.is_type_int(new_src1_type)
    
        new_src2_type,new_src2_value = self.get_type_and_value(src2,src2_type)
        self.is_type_int(new_src2_type)

        try: new_src1_value = int(new_src1_value)
        except ValueError: exit(32)
        try: new_src2_value = int(new_src2_value)
        except ValueError: exit(32)

        match type_of_calc.upper():
            case "ADD":
                dest_value = new_src1_value + new_src2_value
            case "SUB":
                dest_value = new_src1_value - new_src2_value
            case "MUL":
                dest_value = new_src1_value * new_src2_value
            case "IDIV":
                if new_src2_value == 0:
                    exit(57) # dividing by zero
                dest_value = new_src1_value // new_src2_value
            case other:
                exit(52) # unknown type of calculation
        self.assign(dest,dest_value,"INT")
            
    def relation_operators(self,type_of_oper,dest,src1,src1_type,src2,src2_type):
        self.is_initialized(dest)

        new_src1_type,src1_value = self.get_type_and_value(src1,src1_type)
        new_src2_type,src2_value = self.get_type_and_value(src2,src2_type)
        
        
        new_value = "false"
        new_type = "BOOL"
        if new_src1_type.upper() != new_src2_type.upper():
            if type_of_oper.upper() == 'EQ':
                if new_src1_type.upper() == "NIL" or new_src2_type.upper() == "NIL":
                    self.assign(dest,new_value,new_type)
                else:
                    exit(53) # type of args are not same, none of them is nil
            else:
                exit(53) # type of args are not same, not in EQ instruction

        src1_value = self.get_value_to_comparison(src1_value,new_src1_type)
        src2_value = self.get_value_to_comparison(src2_value,new_src2_type)
        if type_of_oper != "EQ":
            if self.is_type_nil(new_src1_type) or self.is_type_nil(new_src2_type):
                exit(53)

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
                exit(53) # unknown instruction
        self.assign(dest,new_value,new_type)

    def bool_operators(self,type_of_oper,dest,src1,src1_type,src2,src2_type):
        new_value = "false"
        new_type = "BOOL"
        self.is_initialized(dest)

        new_src1_type,new_src1_value = self.get_type_and_value(src1,src1_type)

        if new_src1_type.upper() not in ['BOOL']:
            exit(53) # type is not bool
        if new_src1_value == "true":
            new_src1_value = True
        else:
            new_src1_value = False

        if type_of_oper.upper() != "NOT":
            new_src2_type,new_src2_value = self.get_type_and_value(src2,src2_type)
            if new_src2_type.upper() not in ['BOOL']:
                exit(53) # type is not bool
        else:
            if new_src1_value:
                self.assign(dest,"false","BOOL")
            else:
                self.assign(dest,"true","BOOL")
            return

        if new_src2_value == "true":
            new_src2_value = True
        else:
            new_src2_value = False

        match type_of_oper.upper():
            case "AND":
                if new_src1_value and new_src2_value:
                    new_value = "true"
            case "OR":
                if new_src1_value != False or new_src2_value != False:
                    new_value = "true"
                    
            case other:
                exit(52) # unknown instruction
        self.assign(dest,new_value,new_type)

    def write(self,to_write,to_write_type,output=sys.stdout):
        new_type,new_value = self.get_type_and_value(to_write,to_write_type)
        match new_type.upper():
            case "INT":
                print(new_value,end='',file=output)
            case "BOOL":
                if new_value == "true":
                    print("true",end='',file=output)
                else:
                    print("false",end='',file=output)
            case "NIL":
                print("",end='',file=output)
            case "STRING":
                substrings = self.remove_escape_sequence(new_value)
                if substrings == None: # String without escape sequences
                    return
                for substr in substrings:
                    print(substr,end='',file=output)
            case other:
                exit(53) # unknown opcode

    def remove_escape_sequence(self,string_to_modify):
        """
        Function removes escape sequences
        @return: List of strings without escape sequences
        """
        buffer = string_to_modify.split('\\')
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
        print("\tData Stack:",file=sys.stderr)
        if self.data_stack.stack_top == -1:
            print("\t\tEMPTY",file=sys.stderr)
        else:
            print("\t\t[TOP]",file=sys.stderr)
            index = self.data_stack.stack_top
            while index > -1:
                print("\t\t[",self.data_stack.stack[index].value,"| type:",self.data_stack.stack[index].var_type,"]",file=sys.stderr)
                index -= 1
            print("\t\t[BOTTOM]",file=sys.stderr)

    def int2char(self,dest,dest_type,src,src_type):
        new_type, new_value = self.get_type_and_value(src,src_type)
        self.is_type_int(new_type)
        try: new_value = chr(int(new_value))
        except ValueError: exit(58) # value is not int
        except OverflowError: exit(58) # int out of range
        self.is_initialized(dest)
        self.assign(dest,new_value,"STRING")

    def stri2int(self,dest,src1,src1_type,src2,src2_type):
        self.is_initialized(dest)
        src1_new_type, src1_new_value = self.get_type_and_value(src1,src1_type)
        src2_new_type, src2_new_value = self.get_type_and_value(src2,src2_type)
        
        src1_len = len(src1_new_value)
        try: src2_new_value = int(src2_new_value)
        except ValueError: exit(53)
        if src1_len <= src2_new_value or src2_new_value < 0:
            exit(58) # index out of range
        dest_value = ord(src1_new_value[src2_new_value])
        self.assign(dest,dest_value,"INT")

    def read(self,dest,read_type,input_file):
        self.is_initialized(dest)
        if input_file == None: #reading from stdin
            line = sys.stdin.readline()
        else: #reading from file
            line = input_file.readline()
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
                    value = line.replace('\n','')
                    value = value.replace('\\',"\\092")
                    new_type = "STRING"
                case "BOOL":
                    # print("\"",line,"\"")
                    if line.lstrip().rstrip().lower() == "true":
                        value = "true"
                    else:
                        value = "false"
                    new_type = "BOOL"
                case other:
                    exit(52) # unknown opcode
        self.assign(dest,value,new_type.upper())
        return input_file

    def concat(self,dest,src1,src1_type,src2,src2_type):
        self.is_initialized(dest)
        
        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        self.is_type_string(new_src1_type)

        new_src2_type, new_src2_val = self.get_type_and_value(src2,src2_type)
        self.is_type_string(new_src2_type)

        if new_src1_val == None:
            new_src1_val = ""
        if new_src2_val == None:
            new_src2_val = ""
        dest_value = new_src1_val + new_src2_val
        self.assign(dest,dest_value,"STRING")

    def strlen(self,dest,src1,src1_type):
        self.is_initialized(dest)

        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        self.is_type_string(new_src1_type)

        dest_value = len(new_src1_val)
        self.assign(dest,dest_value,"INT")
        
    def getchar(self,dest,src1,src1_type,src2,src2_type):
        self.is_initialized(dest)
        
        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        self.is_type_string(new_src1_type)

        new_src2_type, new_src2_val = self.get_type_and_value(src2,src2_type)
        self.is_type_int(new_src2_type)

        new_src1_len = len(new_src1_val)
        try: new_src2_val = int(new_src2_val)
        except ValueError: exit(53)
        if new_src1_len <= new_src2_val or new_src2_val < 0:
            exit(58)
        dest_value = new_src1_val[new_src2_val]
        self.assign(dest,dest_value,"STRING")

    def setchar(self,dest,src1,src1_type,src2,src2_type):
        new_dest_type, new_dest_val = self.get_type_and_value(dest,"VAR")
        self.is_type_string(new_dest_type)

        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        self.is_type_int(new_src1_type)

        new_src2_type, new_src2_val = self.get_type_and_value(src2,src2_type)
        self.is_type_string(new_src2_type)

        list1 = self.remove_escape_sequence(new_src2_val)
        new_src2_val = ""
        for substring in list1:
            new_src2_val = new_src2_val + substring

        new_src2_len = len(new_src2_val)
        if not new_src2_len:
            exit(58)
        new_dest_len = len(new_dest_val)
        try: new_src1_val = int(new_src1_val)
        except ValueError: exit(53)
        if new_dest_len <= new_src1_val or new_src1_val < 0:
            exit(58)
        new_dest_val = new_dest_val[:new_src1_val] + new_src2_val[0] + new_dest_val[new_src1_val+1:]
        self.assign(dest,new_dest_val,"STRING")
    
    def jumpifeq(self,dest,src1,src1_type,src2,src2_type,call_stack,order_dict,instr_index,neq):
        if dest not in call_stack.label_list:
            exit(52)
            
        new_src1_type,new_src1_value = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() not in ['INT','BOOL','STRING','NIL']:
            exit(53)
        
        new_src2_type,new_src2_value = self.get_type_and_value(src2,src2_type)
        if new_src2_type.upper() not in ['INT','BOOL','STRING','NIL']:
            exit(53)
        
        new_value = False
        new_src1_value = self.get_value_to_comparison(new_src1_value,new_src1_type)
        new_src2_value = self.get_value_to_comparison(new_src2_value,new_src2_type)
        if new_src1_type.upper() != new_src2_type.upper():
            if self.is_type_nil(new_src1_type) or self.is_type_nil(new_src2_type):
                new_value = False
            else:
                exit(53)
        else:
            if new_src1_value == new_src2_value:
                new_value = True
            else:
                new_value = False

        if neq:
            new_value = not new_value

        if new_value:
            new_instr_index = order_dict[call_stack.label_order[dest]]
            return new_instr_index
        return instr_index

    def is_type_int(self,type_to_check):
        if type_to_check.upper() != "INT":
            exit(53)

    def is_type_string(self,type_to_check):
        if type_to_check.upper() != "STRING":
            exit(53)
    
    def get_bool_value(self,bool_val):
        if bool_val.lower() == "true":
            return True
        return False
    
    def is_type_nil(self,type_to_check):
        if type_to_check.lower() == "nil":
            return True
        return False

    def get_value_to_comparison(self,src,src_type):
        match src_type.upper():
            case "INT":
                src_ret = int(src)
            case "STRING":
                list1 = self.remove_escape_sequence(src)
                src_ret = ""
                for string in list1:
                    src_ret = src_ret + string
            case "BOOL":
                src_ret = self.get_bool_value(src)
            case "NIL":
                src_ret = "nil"
        return src_ret

    def comparison(self,src1,src1_type,src2,src2_type):
        if self.is_type_nil(src1_type) and self.is_type_nil(src2_type):
            return True
        elif self.is_type_nil(src1_type):
            match src2_type.upper():
                case "STRING":
                    if src2 == "":
                        return True
                case "INT":
                    if src2 == 0:
                        return True
                case "BOOL":
                    if src2 == False:
                        return True
        elif self.is_type_nil(src2_type):
            match src1_type.upper():
                case "STRING":
                        if src2 == "":
                            return True
                case "INT":
                    if src2 == 0:
                        return True
                case "BOOL":
                    if src2 == False:
                        return True
        return False