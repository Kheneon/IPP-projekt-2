class Variable:
    def __init__(self,name):
        self.name = name
        self.var_type = "none"
        self.value = None

    def assign(self,value,var_type):
        self.value = value
        self.var_type = var_type