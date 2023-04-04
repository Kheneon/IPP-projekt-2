#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   FrameClass.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
from VariableClass import *

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
            exit(52) # variable has no name TODO: errcode
        if name in self.var_list:
            exit(52) # redefinition of variable
        self.variables.append(Variable(name))
        self.var_list.append(name)

    def write_var(self):
        for var in self.variables:
            print("\t[name]",var.name,"[type]",var.var_type,"[value]",var.value)