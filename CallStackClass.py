class CallStack:
    """Holds positions that we will return to"""
    def __init__(self):
        self.label_order = {}
        self.label_list = []
        self.stack = []
        self.stack_top = -1
    
    def pop(self):
        if self.stack_top == -1:
            exit(1) # Call stack is empty TODO: exit code
        order = self.stack.pop()
        self.stack_top -= 1
        return order

    def push(self,order):
        self.stack.append(order)
        self.stack_top += 1
    
    def add_label(self,name,order):
        self.label_order[name] = order
        self.label_list.append(name)