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
