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
