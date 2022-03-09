class Stack():
    def __init__(self) -> None:
        self.array = []
        self.top = -1

    def empty(self):
        return True if self.top == -1 else False

    def peek(self):
        return self.array[-1]

    def pop(self):
        if not self.empty():
            self.top -= 1
            return self.array.pop()
        else:
            return None
    
    def push(self, val):
        self.top += 1
        self.array.append(val)


    def __str__(self) -> str:
        return self.array