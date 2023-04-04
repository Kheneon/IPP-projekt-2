#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   CallStackClass.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
class CallStack:
    """Holds positions that we will return to"""
    def __init__(self):
        self.label_order = {}
        self.label_list = []
        self.stack = []
        self.stack_top = -1
    
    def pop(self):
        if self.stack_top == -1:
            exit(56) # Call stack is empty
        order = self.stack.pop()
        self.stack_top -= 1
        return order

    def push(self,order):
        self.stack.append(order)
        self.stack_top += 1
    
    def add_label(self,name,order):
        self.label_order[name] = order
        self.label_list.append(name)