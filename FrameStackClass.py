#########################################
#
# IPP projekt 2
# Date:    2022/2023
#
# Modul:   FrameStackClass.py
#
# Author:  Michal Zapletal
# Contact: xzaple41@stud.fit.vutbr.cz
#
#########################################
from FrameClass import *

class FrameStack:
    def __init__(self):
        self.global_frame = Frame(True) #Global
        self.local_frame = Frame(False) #Local
        self.temp_frame = Frame(False)  #Temporary
        self.stack = []                 #Empty stack
        self.stack_top = -1

    def create_frame(self):
        """Creating temporary frame"""
        self.temp_frame = Frame(True)

    def pop_frame(self):
        """Pops Local frame to Temporary frame, remove previous Temporary frame"""
        if self.stack_top == -1:
            exit(55) # no frame to pop from stack left

        self.temp_frame = self.local_frame
        self.local_frame = self.stack[self.stack_top] 
        self.stack_top -= 1
        self.stack.pop()

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