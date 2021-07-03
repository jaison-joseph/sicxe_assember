registers = {
    "A" : ("0" , "24"),
    "X" : ("1" , "24"),
    "L" : ("2" , "24"),
    "B" : ("3" , "48"),
    "S" : ("4" , "48"),
    "T" : ("5" , "48"),
    "F" : ("6" , "48"),
    "PC": ("8" , "24"),
    "SW": ("9" , "24")
}

print(registers.keys())
print(registers['F'])
print(registers['F'][0])
print(type(registers['F'][0]))

a = [i for i in range(5)]
print("before:", a)
for ele in a:
    ele += 2
print("after:", a)

class jj():

    def __init__(self, input):
        self.number = input

array = [jj(i) for i in range(5)]
for index, h in enumerate(array):
    h.number += 10

for obj in array:
    print(obj.__dict__)

def add(num):
    num += 1

num = 3
add(num)
print("num:", num)
