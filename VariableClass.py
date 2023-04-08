#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   VariableClass.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
class Variable:
    def __init__(self,name):
        self.name = name
        self.var_type = None
        self.value = None

    def assign(self,value,var_type):
        self.value = value
        self.var_type = var_type