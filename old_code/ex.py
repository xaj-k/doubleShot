class CanInc():
    def __init__(self, initialValue):
        self.m = initialValue
    def inc(self):
        self.m += 1
    def dec(self):
        self.m -= 1

class Ex():
    def __init__(self,x):
        self.x = x
    def getVal(self):
        return self.x


a = CanInc(3)
ex = Ex(a.m)
print("a is %i" % ex.getVal())
a.inc()
print("a is %i" % ex.getVal())