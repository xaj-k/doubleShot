
class Stuff():
    def __init__(self):
        self.a = 0

def addOne(stuff):
    stuff.a += 1

def minusOne(stuff):
    stuff.a -= 1

if __name__ == "__main__":
    s = Stuff()
    print("stuff.a = %u"%s.a)
    addOne(s)
    print("stuff.a = %u"%s.a)
    addOne(s)
    print("stuff.a = %u"%s.a)
    minusOne(s)
    print("stuff.a = %u"%s.a)