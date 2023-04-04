#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   DataStackClass.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
from VariableClass import *

class DataStack:
    def __init__(self):
        self.stack = []
        self.stack_top = -1
    
    def pop(self):
        if self.stack_top < 0:
            exit(56) # empty data stack
        self.stack_top -= 1
        return self.stack.pop()

    def push(self,value,var_type):
        var = Variable(None)
        var.assign(value,var_type)
        self.stack.append(var)
        self.stack_top += 1

    def write_data_stack(self):
        print("[DEBUG] --- DATA STACK ---\n[TOP]")
        for var in self.stack:
            print("[TYPE] ",var.var_type," [VALUE] ",var.value)
        print("[BOTTOM]")