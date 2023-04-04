from FrameStackClass import *
from DataStackClass import *
import sys

instr_index = 0
file = None

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
        #self.call_stack = CallStack()

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
            new_type,new_value = self.get_type_and_value(instruction[1].text,instruction[0].attrib.get('type'))
        else: # int, string, bool, nil
            new_type = instruction[1].attrib.get('type').upper()
            if new_type not in ['STRING','BOOL','NIL','INT']:
                exit(1) #TODO: errcode
            new_value = instruction[1].text
        self.assign(instruction[0].text,new_value,new_type)

    def to_type(self,dest,src,src_type):
        """
        Function takes on input
        @param: dest Name of variable. Where to save result of operation
        @param: src  Scans this variable and constant, type saves into dest
        """
        if self.is_initialized(dest) == False:
            exit(1)
        new_value,new_type = self.get_type_and_value(src,src_type)
        new_type = "STRING"
        self.assign(dest,new_value.lower(),new_type)

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

    def get_type_and_value(self,variable,variable_type):
        """
        Function returns Type and Value of variable\n
        If it is not variable, but constant, returns constant\n
        Exits program if frames are not initialized\n
        Exits program if variable is uninitialized
        """
        if variable_type.upper() != "VAR":
            return variable_type,variable
        if self.is_assigned(variable) == False:
            exit(1)
        if variable[0:3] == "GF@":
            variables = self.frame_stack.global_frame.variables
        elif variable[0:3] == "LF@":
            if self.frame_stack.local_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            variables = self.frame_stack.local_frame.variables
        elif variable[0:3] == "TF@":
            if self.frame_stack.temp_frame.initialized == False:
                exit(1) #uninitalized frame TODO: errcode
            variables = self.frame_stack.temp_frame.variables
        for var in variables:
            if variable[3:] == var.name:
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
        new_type,new_value = self.get_type_and_value(value,var_type)
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
        new_src1_type,new_src1_value = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() != "INT":
            exit(1) #TODO:errcode
    
        new_src2_type,new_src2_value = self.get_type_and_value(src2,src2_type)
        if new_src2_type.upper() != "INT":
            exit(1) #TODO:errcode 52
        match type_of_calc.upper():
            case 'ADD':
                dest_value = int(new_src1_value) + int(new_src2_value)
            case 'SUB':
                dest_value = int(new_src1_value) - int(new_src2_value)
            case 'MUL':
                dest_value = int(new_src1_value) * int(new_src2_value)
            case 'IDIV':
                dest_value = int(int(new_src1_value) / int(new_src2_value))
            case other:
                exit(1)
        self.assign(dest,dest_value,'INT')
            
    def relation_operators(self,type_of_oper,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1)

        src1_type,src1_value = self.get_type_and_value(src1,src1_type)
        src2_type,src2_value = self.get_type_and_value(src2,src2_type)
        
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

        new_src1_type,new_src1_value = self.get_type_and_value(src1,src1_type)

        if new_src1_type.upper() not in ['BOOL']:
            exit(52) #TODO:errcode 52
        
        if type_of_oper.upper() != "NOT":
            new_src2_type,new_src2_value = self.get_type_and_value(src2,src2_type)
            if new_src2_type.upper() not in ['BOOL']:
                exit(52) #TODO:errcode 52
        else:
            if new_src1_value == "true":
                self.assign(dest,"false","BOOL")
            else:
                self.assign(dest,"true","BOOL")
            return

        match type_of_oper.upper():
            case "AND":
                if new_src1_value == new_src2_value:
                    new_value = "true"
            case "OR":
                if new_src1_value != "false" or new_src2_value != "false":
                    new_value = "true"
                    
            case other:
                exit(1) #TODO:errcode unknown instruction
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
                print("",end='')
            case "STRING":
                substrings = self.remove_escape_sequence(new_value)
                if substrings == None: # String without escape sequences
                    return
                for substr in substrings:
                    print(substr,end='',file=output)
            case other:
                print(new_type)
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
        new_type, new_value = self.get_type_and_value(src,src_type)
        try: new_value = chr(int(new_value))
        except ValueError: exit(4) #TODO:errcode
        except OverflowError: exit(5) #TODO:errcode
        if self.is_initialized(dest) == False:
            exit(1) #TODO:errcode
        self.assign(dest,new_value,new_type.upper())

    def stri2int(self,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1) #TODO:errcode
        src1_new_type, src1_new_value = self.get_type_and_value(src1,src1_type)
        src2_new_type, src2_new_value = self.get_type_and_value(src2,src2_type)
        
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
        
        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() != "STRING":
            exit(1)

        new_src2_type, new_src2_val = self.get_type_and_value(src2,src2_type)
        if new_src2_type.upper() != "STRING":
            exit(1)

        dest_value = new_src1_val + new_src2_val
        self.assign(dest,dest_value,"STRING")

    def strlen(self,dest,src1,src1_type):
        if self.is_initialized(dest) == False:
            exit(1)

        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() != "STRING":
            exit(1)

        dest_value = len(new_src1_val)
        self.assign(dest,dest_value,"INT")
        
    def getchar(self,dest,src1,src1_type,src2,src2_type):
        if self.is_initialized(dest) == False:
            exit(1)
        
        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() != "STRING":
            exit(1)

        new_src2_type, new_src2_val = self.get_type_and_value(src2,src2_type)
        if new_src2_type.upper() != "INT":
            exit(1)

        new_src1_len = len(new_src1_val)
        if new_src1_len <= int(new_src2_val):
            exit(58)
        dest_value = new_src1_val[int(new_src2_val)]
        self.assign(dest,dest_value,"STRING")

    def setchar(self,dest,src1,src1_type,src2,src2_type):
        new_dest_type, new_dest_val = self.get_type_and_value(dest,"VAR")
        if new_dest_type.upper() != "STRING":
            exit(1)

        new_src1_type, new_src1_val = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() != "INT":
            exit(1)

        new_src2_type, new_src2_val = self.get_type_and_value(src2,src2_type)
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
    
    def jumpifeq(self,dest,src1,src1_type,src2,src2_type,call_stack,order_dict,neq=False):
        global instr_index
        if dest not in call_stack.label_list:
            exit(1)
            
        new_src1_type,new_src1_value = self.get_type_and_value(src1,src1_type)
        if new_src1_type.upper() not in ['INT','BOOL','STRING','NIL']:
            exit(52) #TODO:errcode 52
        
        new_src2_type,new_src2_value = self.get_type_and_value(src2,src2_type)
        if new_src2_type.upper() not in ['INT','BOOL','STRING','NIL']:
            exit(52) #TODO:errcode 52
        
        new_value = False
        if new_src1_type != new_src2_type:
            if new_src1_type.upper() == "NIL" or new_src2_type.upper() == "NIL":
                new_value = True
            else:
                exit(1) #TODO:errcode
        else:
            new_value = (new_src1_value == new_src2_value)
        
        if neq:
            new_value = not new_value

        if new_value:
            instr_index = order_dict[call_stack.label_order[dest]]