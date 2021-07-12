import pprint

def init():
    global optable
    global registers
    global directives
    # g.symtab[self.label] = (self.location, "INSTRUCTION", -1, "R", g.current_block)
    global symtab                   # {label: (location, type(INSTRUCTION, WORD),
                                    #          value, type(), block number)}
    global littab                   # { (literal value: (location, block number)) }
    global program_block_details    # {number: name startAddreess length

    global register_x
    global register_b
    global line_objects
    global locctr
    global start_address
    global current_block

    global literalsToProcess

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

    optable = {}

    f = open("optable.txt", encoding='utf8')
    for line in f.readlines()[2:]:
        x = line[:25].split(' ')
        x = [y for y in x if y != '']
        if (len(x) == 3):
            x.insert(1, '0')
        optable[x[0]] = tuple(x[1:])

    directives = ('START', 'END', 'RESW', 'RESB', 'WORD',
    'BYTE', 'BASE', 'USE', 'EQU', 'CSECT', 'LTORG', 'EXTDEF', 'EXTREF')

    symtab = {}
    littab = {}
    program_block_details = {}
    control_section_details = {}
    line_objects = []

    register_b = -1
    register_x = -1
    locctr = 0
    start_address = 0
    current_block = 0

    literalsToProcess = False

#end of init()

def test_vars():
    global optable
    global registers
    global directives
    print("\n testing optable: ")
    for x in optable:
        print(x,":", optable[x])
    print(registers)
    print(directives)

def classify_instructions():
    global optable
    arg_types = set([value[0] for key, value in optable.items()])
    instructions_classified = []
    for arg in arg_types:
        instructions_classified.append([[key, value[1]] for key, value in optable.items() if value[0] == arg])
        print(arg, "::", instructions_classified[-1],"\n\n")


if __name__ == "__main__":
    init()
    test_vars()
    classify_instructions()
    print("\n\n optable part of it \n\n")
    for i, obj in enumerate(optable.items()):
        pprint.pprint(obj)
        if i >= 20:
            break
else:
    init()
